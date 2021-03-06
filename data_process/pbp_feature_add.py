import sys
import os,glob
import numpy as np
import pandas as pd
import calendar
from scipy import stats
import time

def load_pbp_game(datapath):
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
def shot_avgs_calc(pbp_DF,groupbyfields,agg_calcs):
    all_shots=pbp_DF.loc[pbp_DF['EVENTMSGTYPE'].apply(lambda x: x in [1,2])].copy()
    calced_agg=all_shots.groupby(groupbyfields,as_index=False).aggregate(agg_calcs)
    calced_agg['pctg']=calced_agg.apply(lambda row: row['SHOT_MADE_FLAG']/row['SHOT_ATTEMPTED_FLAG'],axis=1)

    return calced_agg;
def zone_best_shooter(player_zone_data):
    min_shot_df=player_zone_data.loc[player_zone_data['SHOT_ATTEMPTED_FLAG']>=20].copy()
    best_shooter = min_shot_df.reset_index().groupby(
        ['SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE'], as_index=False).pctg.idxmax().reset_index()
    best_shooter.columns=['SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE','best_shooter_indx']
    named_best_shooter=min_shot_df.reset_index().loc[best_shooter['best_shooter_indx']].copy()

    return named_best_shooter;

def ft_xy(x,y):
    global xcoord_range
    global ycoord_range
    # print("X: " + str(x) + " Y: " + str(y))
    if np.isnan(x):
        return x,y
    else:
        if x>247 or x<-247:
            x=247
        xbuck=xcoord_range[np.around((x+247+4.94)/9.88,0)-1]
        ybuck=ycoord_range[np.around((y+38+4.94)/9.88,0)-1]
    return xbuck,ybuck

def add_ft_buckets(dataframe):
    return pd.concat((
        dataframe,
        dataframe.apply(
            lambda row: pd.Series(ft_xy(row['LOC_X'],row['LOC_Y']), index=['x_ft','y_ft']), axis=1)),axis=1)
if __name__ == "__main__":
    ### INPUT
    pbp_data_path=sys.argv[1]
    outputpath=sys.argv[2]
    runtype=sys.argv[3]

    ### Init Vars
    xcoord_range=np.arange(-247,247,9.88)+4.94
    ycoord_range = np.arange(-38, 1000, 9.88) + 4.94


    ### Do Work

    startpbpload=time.time()
    if runtype=="update":
        all_pbp_data=load_pbp_game(pbp_data_path)
        # print(all_pbp_data.reset_index().loc[196425])
        all_pbp_data = add_ft_buckets(all_pbp_data.reset_index())
        all_pbp_data.loc[all_pbp_data['EVENTMSGTYPE'].apply(lambda x: x in [1, 2]),].to_csv(
            outputpath + "pbp_agg/shots_pbp.csv", index=False, sep="|")

    else:
        all_pbp_data = pd.read_csv(outputpath + "pbp_agg/shots_pbp.csv",sep="|",index_col=False)
    endpbpload=time.time()
    print(endpbpload-startpbpload)

    #Write Shots:

    #Shots ONly


    zone_shot_avgs=shot_avgs_calc(all_pbp_data,['SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE'],{'SHOT_ATTEMPTED_FLAG':'sum','SHOT_MADE_FLAG':'sum'})
    player_zone_shot_avgs=shot_avgs_calc(all_pbp_data,['PLAYER1_NAME','SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE'],{'SHOT_ATTEMPTED_FLAG':'sum','SHOT_MADE_FLAG':'sum'})
    team_zone_shot_avgs=shot_avgs_calc(all_pbp_data,['PLAYER1_TEAM_NICKNAME','SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE'],{'SHOT_ATTEMPTED_FLAG':'sum','SHOT_MADE_FLAG':'sum'})

    qual_play_zone_avg=player_zone_shot_avgs.loc[player_zone_shot_avgs['SHOT_ATTEMPTED_FLAG']>=5].copy().reset_index()
    zone_info=qual_play_zone_avg.groupby(['SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE'],as_index=False)['pctg'].quantile([.2,.4,.6,.8]).reset_index()
    zone_info.columns=['SHOT_ZONE_BASIC','SHOT_ZONE_AREA','SHOT_ZONE_RANGE','P_20','P_40','P_60','P_80']
    print(zone_info)

    zone_kings=zone_best_shooter(player_zone_shot_avgs)
    # print(zone_kings)

    ###write out
    zone_kings.to_csv(outputpath+"pbp_agg/King_of_the_zone.csv",index=False)
    player_zone_shot_avgs.to_csv(outputpath + "pbp_agg/player_shot_zone_avg.csv", index=False)
    zone_info.to_csv(outputpath + "pbp_agg/zone_info.csv", index=False)
    zone_shot_avgs.to_csv(outputpath + "pbp_agg/zone_avg_info.csv", index=False)




