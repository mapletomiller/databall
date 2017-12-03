
import json
import requests
import game_info_scrap
import sys
import pandas as pd
import time
import os

api_headers = {
    'origin': ('http://stats.nba.com'),
    'user-agent': ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'),
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en')

}

def print_db(printstring,db_type):
    global db_types
    if db_types[db_type]:
        print(printstring)

def manually_add_player_oncourt(gameid,teamid,period):
    print_db("Looking for: "+str(gameid)+"|"+str(teamid)+"|"+str(period),'basics')
    with open("../resources/pbp_lineup_manual_adds.txt") as playeradds:
        next(playeradds)
        playerstoadd=[]
        for row in playeradds:
            man_gameid=row.split("|")[0]
            man_teamid=row.split("|")[1]
            man_period=row.split("|")[2]
            man_player=row.split("|")[3].strip()

            if str(man_gameid)==str(gameid) and \
                    str(man_teamid)==str(teamid) and \
                    str(man_period)==str(period):
                playerstoadd.append(man_player)
                print_db("Found: " + str(man_gameid) + "|" + str(man_teamid) + "|" + str(man_period) + "|" + man_player,
                         'basics')
    return playerstoadd
def manual_sub_load(gameid):
    man_subs={}
    with open("../resources/pbp_lineup_manual_subs.txt") as playersubs:
        next(playersubs)
        for row in playersubs:
            man_gameid=row.split("|")[0]
            teamid = row.split("|")[1]
            eventnum = row.split("|")[2]
            player_subin=row.split("|")[3]
            player_subout=row.split("|")[4].strip()
            if str(gameid) == str(man_gameid):
                man_subs[int(eventnum)]=[teamid,player_subin,player_subout]
    print_db(man_subs,'man_subs')
    return man_subs

def scrape_pbp(game_id,starters,game_info,manual_subs):
    global api_headers
    url="http://stats.nba.com/stats/playbyplayv2/?gameId={gid}&startPeriod=0&endPeriod=14".format(gid=game_id)
    localjson_path = rawpath + "/pbp_json/" + "pbp_" + game_id + ".json"
    data=json_retrieve(localjson_path,url)
    # data = requests.get(url, timeout=15, headers=api_headers).json()
    data_headers=data['resultSets'][0]['headers']
    pbp_DF=pd.DataFrame(columns=data_headers)
    for i in data['resultSets'][0]['rowSet']:
        row=dict(zip(data_headers,i))
        pbp_DF=pbp_DF.append(row,ignore_index=True)
    # headers: [
    #     "GAME_ID",
    #     "EVENTNUM",
    #     "EVENTMSGTYPE",
    #     "EVENTMSGACTIONTYPE",
    #     "PERIOD",
    #     "WCTIMESTRING",
    #     "PCTIMESTRING",
    #     "HOMEDESCRIPTION",
    #     "NEUTRALDESCRIPTION",
    #     "VISITORDESCRIPTION",
    #     "SCORE",
    #     "SCOREMARGIN",
    #     "PERSON1TYPE",
    #     "PLAYER1_ID",
    #     "PLAYER1_NAME",
    #     "PLAYER1_TEAM_ID",
    #     "PLAYER1_TEAM_CITY",
    #     "PLAYER1_TEAM_NICKNAME",
    #     "PLAYER1_TEAM_ABBREVIATION",
    #     "PERSON2TYPE",
    #     "PLAYER2_ID",
    #     "PLAYER2_NAME",
    #     "PLAYER2_TEAM_ID",
    #     "PLAYER2_TEAM_CITY",
    #     "PLAYER2_TEAM_NICKNAME",
    #     "PLAYER2_TEAM_ABBREVIATION",
    #     "PERSON3TYPE",
    #     "PLAYER3_ID",
    #     "PLAYER3_NAME",
    #     "PLAYER3_TEAM_ID",
    #     "PLAYER3_TEAM_CITY",
    #     "PLAYER3_TEAM_NICKNAME",
    #     "PLAYER3_TEAM_ABBREVIATION"
    # ],
    # pbp_DF[pbp_DF['EVENTMSGTYPE'].apply(lambda x: x in [1,2])]
    pbp_DF['HOME_ONCOURT'] = [list(starters.loc[starters['TEAM_ID'] == game_info[1],'PLAYER_NAME'])] * len(pbp_DF)
    pbp_DF['AWAY_ONCOURT'] = [list(starters.loc[starters['TEAM_ID'] == game_info[3],'PLAYER_NAME'])] * len(pbp_DF)
    #
    substitution_oncourt(pbp_DF,starters,game_info,manual_subs)
    # print(pbp_DF.loc[38:44])
    all_shots=pbp_DF.loc[pbp_DF['EVENTMSGTYPE'].apply(lambda x: x in [1,2]),['PLAYER1_ID','PLAYER1_TEAM_ID']].copy().drop_duplicates()
    shotlocs=pd.DataFrame()
    for index,row in all_shots.iterrows():
        # print([game_id,str(int(row['PLAYER1_ID'])),str(int(row['PLAYER1_TEAM_ID']))])
        playershot=scrape_shot_data(game_id,str(int(row['PLAYER1_ID'])),str(int(row['PLAYER1_TEAM_ID'])))
        shotlocs=shotlocs.append(playershot,ignore_index=True)


    pbp_DF_final=pd.merge(pbp_DF,shotlocs,left_on=['GAME_ID','EVENTNUM'],right_on=['GAME_ID','GAME_EVENT_ID'],how="left")
    return pbp_DF_final;

def scrape_box_starter(game_id,box_type):
    global rawpath
    url="http://stats.nba.com/stats/boxscoretraditionalv2/?gameId={gid}&startPeriod=0&endPeriod=14&startRange=0&endRange=2147483647&rangeType=0".format(gid=game_id)
    localjson_path=rawpath+"/box_json/"+"box_traditional_"+game_id+".json"
    # data = requests.get(url, timeout=15, headers=api_headers).json()
    data=json_retrieve(localjson_path,url)
    data_headers = data['resultSets'][0]['headers']
    box_df = pd.DataFrame(columns=data_headers)
    for i in data['resultSets'][0]['rowSet']:
        row = dict(zip(data_headers, i))
        box_df = box_df.append(row, ignore_index=True)

    return box_df;


def scrape_shot_data(game_id,player_id,team_id):
    global api_headers
    url="http://stats.nba.com/stats/shotchartdetail/?leagueId=00&season=2017-18&seasonType=Regular+Season&teamId={tm_id}&playerId={pl_id}&gameId={gm_id}&outcome=&location=&month=0&seasonSegment=&dateFrom=&dateTo=&opponentTeamId=0&vsConference=&vsDivision=&position=&playerPosition=&rookieYear=&gameSegment=&period=0&lastNGames=0&clutchTime=&aheadBehind=&pointDiff=&rangeType=0&startPeriod=1&endPeriod=10&startRange=0&endRange=2147483647&contextFilter=&contextMeasure=FGA".format(gm_id=game_id,tm_id=team_id,pl_id=player_id)
    # print(url)
    localjson_path = rawpath + "/shot_json/" + "shotdata_" + game_id+"_"+player_id + ".json"
    # data = requests.get(url, timeout=15, headers=api_headers).json()
    data = json_retrieve(localjson_path, url)
    data_headers = data['resultSets'][0]['headers']
    shot_DF = pd.DataFrame(columns=data_headers)
    for i in data['resultSets'][0]['rowSet']:
        row=dict(zip(data_headers,i))
        shot_DF=shot_DF.append(row,ignore_index=True)

    return shot_DF;

def json_retrieve(localpath,url):
    if os.path.isfile(localpath):
        with open(localpath,"r") as localjson:
            data=json.load(localjson)
            print_db("Loaded Local: "+localpath,'json_load')
    else:
        data=requests.get(url, timeout=30, headers=api_headers).json()
        time.sleep(1)
        print_db("Pulled API: " + url,'json_load')
        with open(localpath,"w") as localjson:
            json.dump(data,localjson)
    return data
def description_parser(description_text):
    x=('who,what,when')

    return x;
def substitution_oncourt(pbp_dataframe,starters,game_info,manual_subs):
    home_starters=list(starters.loc[starters['TEAM_ID'] == game_info[1],'PLAYER_NAME'])
    away_starters=list(starters.loc[starters['TEAM_ID'] == game_info[3],'PLAYER_NAME'])
    for i in range(0,len(pbp_dataframe)):
        if i != 0:
            hm_currentlineup=pbp_dataframe.loc[i-1,'HOME_ONCOURT'].copy()
            aw_currentlineup = pbp_dataframe.loc[i - 1, 'AWAY_ONCOURT'].copy()
        else:
            hm_currentlineup = pbp_dataframe.loc[i, 'HOME_ONCOURT'].copy()
            aw_currentlineup = pbp_dataframe.loc[i, 'AWAY_ONCOURT'].copy()
        pbp_dataframe.at[i,'HOME_ONCOURT']=hm_currentlineup
        pbp_dataframe.at[i, 'AWAY_ONCOURT'] = aw_currentlineup
        # print(i)
        # print(hm_currentlineup)
        # print(aw_currentlineup)
        if i in manual_subs:
            print_db("FOUND MANUAL SUBSTITUTION: ",'man_subs')
            print_db("AT "+str(i)+" IN: "+manual_subs[i][1]+" OUT: "+manual_subs[i][2],'man_subs')

            if str(game_info[1])==str(manual_subs[i][0]):
                print_db("CURRENT LINEUP: "+"|".join(hm_currentlineup),'man_subs')
                hm_currentlineup.remove(manual_subs[i][2])
                hm_currentlineup.append(manual_subs[i][1])
            elif str(game_info[3])==str(manual_subs[i][0]):
                print_db("CURRENT LINEUP: " + "|".join(aw_currentlineup), 'man_subs')
                aw_currentlineup.remove(manual_subs[i][2])
                aw_currentlineup.append(manual_subs[i][1])

        if pbp_dataframe.loc[i,'EVENTMSGTYPE']==8:
            if pbp_dataframe.loc[i,'HOMEDESCRIPTION'] is not None:
                print_db(pbp_dataframe.loc[i,'HOMEDESCRIPTION']+" at "+str(pbp_dataframe.loc[i,'EVENTNUM']),'lineup')
                print_db(hm_currentlineup, 'lineup_detail')
                if pbp_dataframe.loc[i,'PLAYER2_NAME'] not in hm_currentlineup and \
                                pbp_dataframe.loc[i, 'PLAYER1_NAME']  in hm_currentlineup:
                    hm_currentlineup.remove(pbp_dataframe.loc[i,'PLAYER1_NAME'])
                    hm_currentlineup.append(pbp_dataframe.loc[i,'PLAYER2_NAME'])
                else:
                    substitution_invest.append(
                        [pbp_dataframe.loc[i, 'GAME_ID'], pbp_dataframe.loc[i, 'HOMEDESCRIPTION'],
                         pbp_dataframe.loc[i, 'EVENTNUM']])
            elif pbp_dataframe.loc[i,'VISITORDESCRIPTION'] is not None:
                print_db(pbp_dataframe.loc[i, 'VISITORDESCRIPTION']+" at "+str(pbp_dataframe.loc[i,'EVENTNUM']),'lineup')
                print_db(aw_currentlineup,'lineup_detail')
                if pbp_dataframe.loc[i,'PLAYER2_NAME'] not in aw_currentlineup and \
                                pbp_dataframe.loc[i, 'PLAYER1_NAME']  in aw_currentlineup:
                    aw_currentlineup.remove(pbp_dataframe.loc[i, 'PLAYER1_NAME'])
                    aw_currentlineup.append(pbp_dataframe.loc[i, 'PLAYER2_NAME'])
                else:
                    substitution_invest.append([pbp_dataframe.loc[i,'GAME_ID'],pbp_dataframe.loc[i, 'VISITORDESCRIPTION'],pbp_dataframe.loc[i,'EVENTNUM']])
        elif pbp_dataframe.loc[i,'EVENTMSGTYPE']==13 and i+1<len(pbp_dataframe) and len(pbp_dataframe)>= i+5:
            j=i
            print_db(str(j),'lineup')
            hm_lineup_detected=False
            aw_lineup_detected=False
            aw_foundplayers = []
            aw_known_bench=[]
            hm_foundplayers = []
            hm_known_bench = []
            while (not aw_lineup_detected):
                j+=1
                if pbp_dataframe.loc[j,'EVENTMSGTYPE']==8 and \
                                pbp_dataframe.loc[j,'PLAYER1_TEAM_ID']==game_info[3]:
                    if pbp_dataframe.loc[j,'PLAYER1_NAME'] not in aw_foundplayers and\
                        pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in aw_known_bench:
                        aw_foundplayers.append(pbp_dataframe.loc[j,'PLAYER1_NAME'])
                    if pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in aw_foundplayers and \
                                    pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in aw_known_bench:
                        aw_known_bench.append(pbp_dataframe.loc[j,'PLAYER2_NAME'])
                    if len(aw_foundplayers) == 5:
                        aw_lineup_detected = True
                else:
                    for pl_int in range(1,4):
                        if pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] is not None \
                            and pbp_dataframe.loc[j,'PLAYER{num}_TEAM_ID'.format(num=str(pl_int))]==game_info[3]\
                            and pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] not in aw_foundplayers\
                            and pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] not in aw_known_bench:
                            aw_foundplayers.append(pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))])
                            if len(aw_foundplayers)==5:
                                aw_lineup_detected=True
                                break

                print_db("Known Bench",'lineup')
                print_db(aw_known_bench,'lineup')
                print_db("Found Players",'lineup')
                print_db(aw_foundplayers,'lineup')
                if j+1 == len(pbp_dataframe) and len(aw_foundplayers)<5:
                    print_db("NOT ENOUGH AWAY PLAYERS FOUND GAME: "+str(game_info[2])+" Vs "+str(game_info[4])+" PERIOD: "+str(pbp_dataframe.loc[j,'PERIOD']),'basics')
                    addto_lineup=manually_add_player_oncourt(game_info[0],game_info[3],pbp_dataframe.loc[j,'PERIOD'])
                    print_db("Adding: "+" ".join(addto_lineup),'lineup')
                    aw_foundplayers=aw_foundplayers+addto_lineup
                    if len(aw_foundplayers)==5: aw_lineup_detected=True; break
                if j-i==100: aw_lineup_detected=True
            pbp_dataframe.at[i, 'AWAY_ONCOURT']=aw_foundplayers.copy()
            j=i
            while (not hm_lineup_detected):
                j+=1
                if pbp_dataframe.loc[j,'EVENTMSGTYPE']==8 and pbp_dataframe.loc[j,'PLAYER1_TEAM_ID']==game_info[1]:
                    if pbp_dataframe.loc[j,'PLAYER1_NAME'] not in hm_foundplayers and \
                                    pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in hm_known_bench:
                        hm_foundplayers.append(pbp_dataframe.loc[j,'PLAYER1_NAME'])
                    if pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in hm_foundplayers and \
                                    pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in hm_known_bench:
                        hm_known_bench.append(pbp_dataframe.loc[j,'PLAYER2_NAME'])
                    if len(hm_foundplayers) == 5:
                        hm_lineup_detected = True
                else:
                    for pl_int in range(1,4):
                        if pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] is not None \
                            and pbp_dataframe.loc[j,'PLAYER{num}_TEAM_ID'.format(num=str(pl_int))]==game_info[1]\
                            and pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] not in hm_foundplayers\
                            and pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))] not in hm_known_bench:
                            hm_foundplayers.append(pbp_dataframe.loc[j,'PLAYER{num}_NAME'.format(num=str(pl_int))])
                            if len(hm_foundplayers)==5:
                                hm_lineup_detected=True
                                break

                print_db("Known Bench", 'lineup')
                print_db(hm_known_bench, 'lineup')
                print_db("Found Players", 'lineup')
                print_db(hm_foundplayers, 'lineup')
                if j+1 == len(pbp_dataframe) and len(hm_foundplayers)<5:
                    print_db("NOT ENOUGH HOME PLAYERS FOUND GAME: "+str(game_info[2])+" Vs "+str(game_info[4])+" PERIOD: "+str(pbp_dataframe.loc[j,'PERIOD']),'basics')
                    addto_lineup = manually_add_player_oncourt(game_info[0], game_info[1],
                                                               pbp_dataframe.loc[j, 'PERIOD'])
                    print_db("Adding: "+" ".join(addto_lineup),'lineup')
                    hm_foundplayers = hm_foundplayers + addto_lineup
                    if len(hm_foundplayers) == 5: aw_lineup_detected = True
                if j-i==100: hm_lineup_detected=True; break
            pbp_dataframe.at[i, 'HOME_ONCOURT']=hm_foundplayers.copy()


def on_court_detector(pbp_dataframe,j,game_info,i):
    print_db(str(j), 'lineup')
    hm_lineup_detected = False
    aw_lineup_detected = False
    aw_foundplayers = []
    aw_known_bench = []
    hm_foundplayers = []
    hm_known_bench = []
    while (not aw_lineup_detected):
        j += 1
        if pbp_dataframe.loc[j, 'EVENTMSGTYPE'] == 8 and \
                        pbp_dataframe.loc[j, 'PLAYER1_TEAM_ID'] == game_info[3]:
            if pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in aw_foundplayers and \
                            pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in aw_known_bench:
                aw_foundplayers.append(pbp_dataframe.loc[j, 'PLAYER1_NAME'])
            if pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in aw_foundplayers and \
                            pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in aw_known_bench:
                aw_known_bench.append(pbp_dataframe.loc[j, 'PLAYER2_NAME'])
            if len(aw_foundplayers) == 5:
                aw_lineup_detected = True
        else:
            for pl_int in range(1, 4):
                if pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] is not None \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_TEAM_ID'.format(num=str(pl_int))] == game_info[3] \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] not in aw_foundplayers \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] not in aw_known_bench:
                    aw_foundplayers.append(pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))])
                    if len(aw_foundplayers) == 5:
                        aw_lineup_detected = True
                        break

        print_db("Known Bench", 'lineup')
        print_db(aw_known_bench, 'lineup')
        print_db("Found Players", 'lineup')
        print_db(aw_foundplayers, 'lineup')
        if j + 1 == len(pbp_dataframe) and len(aw_foundplayers) < 5:
            print_db("NOT ENOUGH AWAY PLAYERS FOUND GAME: " + str(game_info[2]) + " Vs " + str(
                game_info[4]) + " PERIOD: " + str(pbp_dataframe.loc[j, 'PERIOD']), 'basics')
            addto_lineup = manually_add_player_oncourt(game_info[0], game_info[3], pbp_dataframe.loc[j, 'PERIOD'])
            print_db("Adding: " + " ".join(addto_lineup), 'lineup')
            aw_foundplayers = aw_foundplayers + addto_lineup
            if len(aw_foundplayers) == 5: aw_lineup_detected = True; break
        if j - i == 100: aw_lineup_detected = True
    pbp_dataframe.at[i, 'AWAY_ONCOURT'] = aw_foundplayers.copy()
    j = i
    while (not hm_lineup_detected):
        j += 1
        if pbp_dataframe.loc[j, 'EVENTMSGTYPE'] == 8 and pbp_dataframe.loc[j, 'PLAYER1_TEAM_ID'] == game_info[1]:
            if pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in hm_foundplayers and \
                            pbp_dataframe.loc[j, 'PLAYER1_NAME'] not in hm_known_bench:
                hm_foundplayers.append(pbp_dataframe.loc[j, 'PLAYER1_NAME'])
            if pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in hm_foundplayers and \
                            pbp_dataframe.loc[j, 'PLAYER2_NAME'] not in hm_known_bench:
                hm_known_bench.append(pbp_dataframe.loc[j, 'PLAYER2_NAME'])
            if len(hm_foundplayers) == 5:
                hm_lineup_detected = True
        else:
            for pl_int in range(1, 4):
                if pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] is not None \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_TEAM_ID'.format(num=str(pl_int))] == game_info[1] \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] not in hm_foundplayers \
                        and pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))] not in hm_known_bench:
                    hm_foundplayers.append(pbp_dataframe.loc[j, 'PLAYER{num}_NAME'.format(num=str(pl_int))])
                    if len(hm_foundplayers) == 5:
                        hm_lineup_detected = True
                        break

        print_db("Known Bench", 'lineup')
        print_db(hm_known_bench, 'lineup')
        print_db("Found Players", 'lineup')
        print_db(hm_foundplayers, 'lineup')
        if j + 1 == len(pbp_dataframe) and len(hm_foundplayers) < 5:
            print_db("NOT ENOUGH HOME PLAYERS FOUND GAME: " + str(game_info[2]) + " Vs " + str(
                game_info[4]) + " PERIOD: " + str(pbp_dataframe.loc[j, 'PERIOD']), 'basics')
            addto_lineup = manually_add_player_oncourt(game_info[0], game_info[1],
                                                       pbp_dataframe.loc[j, 'PERIOD'])
            print_db("Adding: " + " ".join(addto_lineup), 'lineup')
            hm_foundplayers = hm_foundplayers + addto_lineup
            if len(hm_foundplayers) == 5: aw_lineup_detected = True
        if j - i == 100: hm_lineup_detected = True; break
    pbp_dataframe.at[i, 'HOME_ONCOURT'] = hm_foundplayers.copy()






def pull_pbp_date(extractdate,team_info_path,pbpoutput_path,onegame_pull):
    global manual_subs
    team_info = game_info_scrap.load_team_info(team_info_path)
    games_list=game_info_scrap.scrap_scoreboard(extractdate,team_info)
    print("Pulling these Games: ")

    #[Game id, home id, home tri, away team id, away tricode]
    if onegame_pull!="NA":
        games_list=[l for l in games_list if l[0]==onegame_pull]
    for i in games_list:
        print(i)
    for i in games_list:
        manual_subs = manual_sub_load(i[0])
        print('Extracting '+str(i[2])+" vs "+str(i[4]))
        tms_box=time.time()
        box_traditional=scrape_box_starter(i[0],'traditional')
        tme_box=time.time()
        print("Box Extract Time: "+ str(tme_box-tms_box))
        box_traditional.to_csv(pbpoutput_path+"box/box_trad_"+str(i[5])+"_"+str(i[0])+"_"+str(i[2])+str(i[4])+".csv",index=False,na_rep="",float_format='%.0f')
        gamestarters=box_traditional.loc[box_traditional['START_POSITION']!="",['PLAYER_ID','PLAYER_NAME','TEAM_ID']]
        # print(gamestarters)

        tms_pbp=time.time()
        gamepbp=scrape_pbp(i[0],gamestarters,i,manual_subs)
        tme_pbp=time.time()
        print("PBP Extract Time: "+str(tme_pbp-tms_pbp))
        gamepbp.to_csv(pbpoutput_path+"pbp/pbp_"+str(i[5])+"_"+str(i[0])+"_"+str(i[2])+str(i[4])+".txt",index=False,na_rep="",float_format='%.0f',sep="|")

if __name__ == "__main__":
    ### GLobal Vars
    global team_info
    global manual_subs
    pbpoutput=sys.argv[2]
    rundate=sys.argv[3]
    rawpath=pbpoutput+"raw_json"
    db_types={'basics':True,'lineup':False,'json_load':False,'lineup_detail':False,'man_subs':False}
    substitution_invest=[]

    # LOAD TEAM DATA
    team_info_path = sys.argv[1]
    team_info = game_info_scrap.load_team_info(team_info_path)

    ##### TESTING ###############
    # sample_games = game_info_scrap.scrap_scoreboard("10/17/2017",team_info)
    # time.sleep(2)
    # gamepbp=scrape_pbp(sample_games[0][0])
    # print(gamepbp.loc[gamepbp['EVENTMSGTYPE'].apply(lambda x: x in [1,2]),['PLAYER1_ID','PLAYER1_TEAM_ID']].drop_duplicates())
    # gamepbp.to_csv(pbpoutput+"/pbp_"+str(sample_games[0][0])+".csv",na_rep="",index=False)
    ###################


    pull_pbp_date(rundate,team_info_path,pbpoutput,"NA")
    print_db(substitution_invest,'basics')
    # test_shot_scrap=scrape_shot_data("0021700002","201939","1610612744")
    # test_shot_scrap.to_csv(pbpoutput+"shots_sample_steph.csv",index=False,na_rep="")