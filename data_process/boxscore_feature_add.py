####SCRIPT TO ADD DFS SALARIES AND OTHER INDICATORS TO THE DAILY BOXSCORES
### INCLUDING GAME INDEX

import sys
import os,glob
import numpy as np
import pandas as pd
import calendar
from scipy import stats
import time
import re
def load_schedule(month):
    global team_abrvs
    with open("../resources/"+month+"_sched.csv",'r') as monthschedule:
        next(monthschedule)
        games=[]
        for line in monthschedule:
            hometeam=line.split(",")[4].strip()
            awayteam=line.split(",")[2].strip()
            datefull=line.split(",")[0].strip()
            if int(datefull.split(" ")[2]) in [x for x in range(1,10)]:
                dateday="0"+str(datefull.split(" ")[2])
            else:
                dateday=str(datefull.split(" ")[2])
            datefinal=str(datefull.split(" ")[3])+str(month_abrvs[datefull.split(" ")[1]])+dateday
            # print(datefinal)
            hometeam_abr=team_abrvs[hometeam]
            awayteam_abr=team_abrvs[awayteam]
            #print(datefinal+"|"+hometeam_abr+"|"+awayteam_abr)

            # games.append((datefinal,hometeam_abr,awayteam_abr))
            team_sched[hometeam_abr][datefinal]=awayteam_abr
            team_sched[awayteam_abr][datefinal]=hometeam_abr
    return;
def name_fixes(name):
    if name=="J.J. Barea":
        fixed_name="Jose Barea"
    elif name=="Wesley Matthews":
        fixed_name="Wes Matthews"
    elif name=="Dennis Smith":
        fixed_name="Dennis Smith Jr."
    elif name=="Lou Williams":
        fixed_name="Louis Williams"
    elif name=="Tim Hardaway":
        fixed_name="Tim Hardaway Jr."
    elif name== "Willy Hernangomez":
        fixed_name="Guillermo Hernangomez"
    elif name== "Juan Hernangomez":
        fixed_name="Juancho Hernangomez"
    elif name== "Larry Nance":
        fixed_name="Larry Nance Jr."
    elif name== "Kelly Oubre":
        fixed_name="Kelly Oubre Jr."
    elif name=="Luc Mbah a Moute":
        fixed_name="Luc Richard Mbah a Moute"
    elif name == "Taurean Waller-Prince":
        fixed_name="Taurean Prince"
    else:
        fixed_name=name
    return fixed_name;
def abbrev_fix(abbrev):
    if abbrev=="BKN":
        final="BRK"
    elif abbrev=="CHA":
        final="CHO"
    elif abbrev=="NOR":
        final="NOP"
    elif abbrev == "NO":
        final="NOP"
    elif abbrev == "GS":
        final="GSW"
    elif abbrev=="SA":
        final="SAS"
    elif abbrev=="NY":
        final="NYK"
    else:
        final=abbrev
    return final;
def attach_alt_name(box_name):
    dfs_name = box_name.split(",")[1].strip() + " " + box_name.split(",")[0].strip()
    final_name=name_fixes(dfs_name)
    return final_name;
def load_individual_game(datapath):
    all_games="first_file"
    for file in glob.glob(datapath+"*.txt"):
        x=pd.read_csv(file,sep="|")
        if type(all_games) is str:
            # print(file)
            all_games=x
        else:
            # print("Adding:")
            # print(x)
            all_games=all_games.append(x)
    return all_games;
def combine_dfs_days(datapath):
    global team_sched
    print(team_sched['HOU'])
    all_days = "first_file"
    for file in glob.glob(datapath + "DKSalaries*"):
        x = pd.read_csv(file, sep=",")
        filename=file.split("/")[9]
        # print(filename)
        gamedate=re.search('^(DKSalaries_)([0-9]{8})(.*)',filename).group(2)
        x['GameDate']=gamedate
        x['teamAbbrev']=x.teamAbbrev.apply(lambda x: x.upper())
        x['opp_team']=x.apply(lambda row: team_sched[abbrev_fix(row['teamAbbrev'])][row['GameDate']],axis=1)
        if type(all_days) is str:
            # print(file)
            all_days = x

        else:
            # print("Adding:")
            # print(x)
            all_days = all_days.append(x)

    # all_days['gameDate']=all_days.GameInfo.apply(lambda x: x.split(' ')[1])
    all_days.to_csv(datapath+"all_days.csv",index=False,na_rep="")
def process_mp(mpstring):
    mins=mpstring.split(":")[0]
    secs=mpstring.split(":")[1]
    final=int(mins)+(int(secs)/60)
    return final;
def cal_dfs_points(Points, Rebounds, Assists, Blocks, Steals,Threes,TOV):
    dfs_points=Points+(Threes*.5)+(Rebounds*1.25)+(Assists*1.5)+(Steals*2)+(Blocks*2)+(TOV*-.5)
    bonus_points=bonus_check(Points, Rebounds, Assists, Blocks, Steals)
    return dfs_points+bonus_points;
def calc_gamescore(Points, OREB,DREB,FGM,FGA,FTA,FTM, AST, BLK, STL,TO,PF):
    gamescore=(Points * 1.0) + (FGM * 0.4) + (FGA * -0.7) + ((FTA-FTM) * -0.4) +(OREB * 0.7) + (DREB * 0.3) + (STL * 1.0) + (AST * 0.7) + (BLK * 0.7) + (PF * -0.4) + (TO * -1.0)
    return gamescore;
def bonus_check(Points, Rebounds, Assists, Blocks, Steals):
    stats=[Points, Rebounds, Assists, Blocks, Steals]
    count_doubledig=len([i for i in stats if i>=10])
    if count_doubledig ==2:
        points=1.5
    elif count_doubledig>=3:
        points=4.5
    else:
        points=0
    return points;
def calc_player_avg(allgamebox):
    # FILTER OUT GAMES NOT PLAYED
    playedgames=allgamebox.loc[allgamebox.mp.notnull()].copy()
    playedgames['mp_num']=playedgames.apply(lambda row: process_mp(row['mp']),axis=1)
    playedgames['def_comb']=playedgames['blk']+playedgames['stl']
    grouped_playedgames=playedgames.groupby(['player_name','team'],as_index=False)
    count_of_games=grouped_playedgames.mp.agg({"gamecount":'count'}) #MP instead of date
    aggregated=grouped_playedgames.aggregate('mean')
    counting_columns=aggregated[['player_name','team','dfs_salary', 'mp_num', 'fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'pts', 'drb', 'orb', 'trb', 'ast', 'stl', 'blk', 'def_comb','tov', 'pf', 'plus_minus', 'efg_pct', 'ts_pct', 'orb_pct', 'drb_pct', 'trb_pct', 'ast_pct', 'stl_pct', 'blk_pct', 'tov_pct', 'off_rtg', 'def_rtg', 'usg_pct', 'dfs_points','gamescore']]
    final_df=pd.merge(counting_columns,count_of_games,on=['player_name','team'])
    return final_df;
def calc_metric_scale(metric,metric_val):
    if metric_scale_type[metric]=="pct_max":
        met_scalar=(metric_val/qual_players[metric].max())
    elif metric_scale_type[metric]=="rank":
        met_scalar=stats.percentileofscore(qual_players[metric], metric_val)/100
    else:
        met_scalar="error"
    return met_scalar;

def calc_position_avg(position):
    global qual_with_pos

    position_only=rotation_with_pos.loc[rotation_with_pos.dfs_position.isnull().apply(lambda x: not x)]
    right_position=position_only.loc[(position_only.dfs_position.apply(lambda x: position in x))].copy().reset_index()
    if position == "C":
        print(right_position)
    position_mean=right_position.mean()
    return position_mean;

def calc_coords(metric,metric_val,pent_pos,x_y):
    ### Get scale
    global qual_players

    metric_scalar=calc_metric_scale(metric,metric_val)
    final_coords=[x*(metric_scalar) for x in radar_coords[pent_pos]]
    if x_y=="x":
        coord=final_coords[0]+radar_coords['center'][0]
    else:
        coord=final_coords[1]+radar_coords['center'][1]
    return coord;

def create_coord_cols(metrics,met_dataframe,melt):
    if melt=="y":
        lean_df=met_dataframe[['player_name','team']+metrics]
        tall_met_df=pd.melt(lean_df,['player_name','team'])
    else:
        tall_met_df=met_dataframe.copy()
    tall_met_df['x']=tall_met_df.apply(
        lambda row: calc_coords(row['variable'],row['value'],basic_pent_pos[row['variable']],"x"),axis=1)
    tall_met_df['y'] = tall_met_df.apply(
        lambda row: calc_coords(row['variable'], row['value'], basic_pent_pos[row['variable']], "y"), axis=1)
    tall_met_df['path_order']=tall_met_df.apply(lambda row: radar_coords[basic_pent_pos[row['variable']]][2],axis=1)
    pts_douplines=tall_met_df.loc[tall_met_df['variable']=='pts'].copy()
    pts_douplines['path_order']=6
    final_df=tall_met_df.append(pts_douplines)
    return final_df;
if __name__ == "__main__":
    ###
    ###INIT VARS ###
    starttime=time.time()
    boxscore_data_path=sys.argv[1]
    outputpath=sys.argv[2]
    dfs_datapath=sys.argv[3]
    team_sched = {}

    team_abrvs = {}
    with open("../resources/" + "Team_abrevs.csv", 'r') as abrvs_file:
        for line in abrvs_file:
            team_abrvs[line.split(',')[0].strip()] = str(line.split(',')[1].strip())
            team_sched[line.split(',')[1].strip()] = {}
    all_game_data=load_individual_game(boxscore_data_path)

    month_abrvs = {v: k for k, v in enumerate(calendar.month_abbr)}

    load_schedule('full')

    player_positions=['PG','SG','SF','PF','C','G','F']
    radar_coords={'top':[0,272,1],'top_left':[-248,83,5],"bot_left":[-154,-223,4],'bot_right':[154,-223,3],'top_right':[248,83,2],'center':[340,311,99]}
    basic_pent_pos={'pts':'top','ast':'top_right','trb':'bot_right','def_comb':'bot_left','gamescore':'top_left'}
    metric_scale_type={"pts":"pct_max","ast":"pct_max","trb":"pct_max","def_comb":"pct_max","gamescore":"pct_max"}

    # print(all_game_data.apply(lambda row: cal_dfs_points(row['pts'],row['trb'],row['ast'],row['blk'],row['stl'],row['fg3'],row['tov']),axis=1))

    ####
    all_game_data['dfs_points']=all_game_data.apply(lambda row: cal_dfs_points(row['pts'],row['trb'],row['ast'],row['blk'],row['stl'],row['fg3'],row['tov']),axis=1)
    ### Calc Game Score
    # (Points, OREB, DREB, FGM, FGA, FTA, FTM, AST, BLK, STL, TO, PF):
    all_game_data['gamescore'] = all_game_data.apply(
        lambda row: calc_gamescore(row['pts'], row['orb'], row['drb'], row['fg'], row['fga'], row['fta'], row['ft'],row['ast'],row['blk'],row['stl'],row['tov'],row['pf']),axis=1)
    ### Attach Alt Name
    all_game_data['alt_name']=all_game_data['player_name'].apply(lambda x: attach_alt_name(x))


    #### WRITE COMBINED BOXES
    all_game_data.to_csv(boxscore_data_path+"/combined/all_boxscores.csv",index=False,na_rep="NA")
    # print(list(all_game_data))

    #Player Averages
    player_aggs=calc_player_avg(all_game_data)
    # print(player_aggs.head(5))
    # Get Penta Filtered Scale
    qual_players=player_aggs.loc[(player_aggs['gamecount']>3) & (player_aggs['mp_num']>=5)].copy()
    rotation_players=player_aggs.loc[(player_aggs['gamecount']>1) & (player_aggs['mp_num']>=25)].copy()
    # print(player_maxes)
    ###Get Player position
    max_positions = all_game_data.loc[all_game_data['dfs_position'].notnull()].reset_index().groupby(['player_name', 'team'], as_index=False).date.idxmax().reset_index()
    max_positions.columns = ['player_name', 'team', 'latest_date_index']
    latest_positions = all_game_data.reset_index().loc[max_positions['latest_date_index']]
    rotation_with_pos = pd.merge(rotation_players, latest_positions[['player_name', 'team', 'dfs_position']],
                             on=['player_name', 'team'],copy=False)
    # latest_positions.to_csv(outputpath+"players_max_position.csv",index=False)
    # qual_with_pos.to_csv(outputpath+"players_with_position.csv",index=False)
    #Get Position Avgs
    pos_averages=""
    for pos in player_positions:
        pos_means=calc_position_avg(pos).copy()
        pos_means=pos_means.reset_index()
        pos_means.columns=['variable','value']
        pos_means['player_name']=pos
        pos_means['team']='position_avg'
        print(pos)
        if pos=="C":
            print(pos_means)
        if pos != "PG":
            pos_averages=pos_averages.append(pos_means)
        else:
            pos_averages=pos_means.copy()

    #Basic Pent Position Averages
    basic_position_avg=pos_averages.loc[pos_averages['variable'].apply(lambda x: x in basic_pent_pos.keys())]

    ##Get Player Coords
    player_coords=create_coord_cols(['pts','trb','ast','def_comb','gamescore'],player_aggs,"y")
    pos_avg_coords=create_coord_cols(['pts','trb','ast','def_comb','gamescore'],basic_position_avg,"n")
    # print(player_coords.loc[player_coords['player_name']=="Curry,Stephen"])
    player_coords.append(pos_avg_coords).to_csv(outputpath+"basic_pent_data.csv",index=False,na_rep="NA")
    pos_avg_coords.to_csv(outputpath+"pos_avg_data.csv",index=False,na_rep="NA")
    # combine_dfs_days(dfs_datapath)
    endtime=time.time()

    print("Runtime: "+str(endtime-starttime))