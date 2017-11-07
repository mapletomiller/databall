
import json
import requests
import game_info_scrap
import sys
import pandas as pd
import time

api_headers = {
    'origin': ('http://stats.nba.com'),
    'user-agent': ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'),
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en')

}
def scrape_pbp(game_id,starters,game_info):
    global api_headers
    url="http://stats.nba.com/stats/playbyplayv2/?gameId={gid}&startPeriod=0&endPeriod=14".format(gid=game_id)
    data = requests.get(url, timeout=5, headers=api_headers).json()
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
    substitution_oncourt(pbp_DF,starters,game_info)
    print(pbp_DF.loc[38:44])
    sys.exit()
    all_shots=pbp_DF.loc[pbp_DF['EVENTMSGTYPE'].apply(lambda x: x in [1,2]),['PLAYER1_ID','PLAYER1_TEAM_ID']].copy().drop_duplicates()
    shotlocs=pd.DataFrame()
    for index,row in all_shots.iterrows():
        # print([game_id,str(int(row['PLAYER1_ID'])),str(int(row['PLAYER1_TEAM_ID']))])
        playershot=scrape_shot_data(game_id,str(int(row['PLAYER1_ID'])),str(int(row['PLAYER1_TEAM_ID'])))
        shotlocs=shotlocs.append(playershot,ignore_index=True)
        time.sleep(1)

    pbp_DF_final=pd.merge(pbp_DF,shotlocs,left_on=['GAME_ID','EVENTNUM'],right_on=['GAME_ID','GAME_EVENT_ID'],how="left")
    return pbp_DF_final;

def scrape_box_starter(game_id,box_type):
    url="http://stats.nba.com/stats/boxscoretraditionalv2/?gameId={gid}&startPeriod=0&endPeriod=14&startRange=0&endRange=2147483647&rangeType=0".format(gid=game_id)
    data = requests.get(url, timeout=5, headers=api_headers).json()
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
    data = requests.get(url, timeout=5, headers=api_headers).json()
    data_headers = data['resultSets'][0]['headers']
    shot_DF = pd.DataFrame(columns=data_headers)
    for i in data['resultSets'][0]['rowSet']:
        row=dict(zip(data_headers,i))
        shot_DF=shot_DF.append(row,ignore_index=True)

    return shot_DF;

def description_parser(description_text):
    x=('who,what,when')

    return x;
def substitution_oncourt(pbp_dataframe,starters,game_info):
    for i in range(0,len(pbp_dataframe)):
        if i != 0:
            hm_currentlineup=pbp_dataframe.loc[i-1,'HOME_ONCOURT'].copy()
            aw_currentlineup = pbp_dataframe.loc[i - 1, 'AWAY_ONCOURT'].copy()
        else:
            hm_currentlineup = pbp_dataframe.loc[i, 'HOME_ONCOURT'].copy()
            aw_currentlineup = pbp_dataframe.loc[i, 'AWAY_ONCOURT'].copy()
        pbp_dataframe.at[i,'HOME_ONCOURT']=hm_currentlineup
        pbp_dataframe.at[i, 'AWAY_ONCOURT'] = aw_currentlineup
        print(i)
        # print(hm_currentlineup)
        print(aw_currentlineup)
        if pbp_dataframe.loc[i,'EVENTMSGTYPE']==8:
            if pbp_dataframe.loc[i,'HOMEDESCRIPTION'] is not None:
                print(pbp_dataframe.loc[i,'HOMEDESCRIPTION'])
                hm_currentlineup.remove(pbp_dataframe.loc[i,'PLAYER1_NAME'])
                hm_currentlineup.append(pbp_dataframe.loc[i,'PLAYER2_NAME'])
            elif pbp_dataframe.loc[i,'VISITORDESCRIPTION'] is not None:
                print(pbp_dataframe.loc[i, 'VISITORDESCRIPTION'])
                aw_currentlineup.remove(pbp_dataframe.loc[i, 'PLAYER1_NAME'])
                aw_currentlineup.append(pbp_dataframe.loc[i, 'PLAYER2_NAME'])
        elif pbp_dataframe.loc[i,'EVENTMSGTYPE']==13 and pbp_dataframe.loc[i,'PERIOD']!=4:
            j=i
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
                    if pbp_dataframe.loc[j,'PLAYER1_NAME'] not in aw_foundplayers:
                        aw_foundplayers.append(pbp_dataframe.loc[j,'PLAYER1_NAME'])
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

                print("Known Bench")
                print(aw_known_bench)
                print("Found Players")
                print(aw_foundplayers)
                if j-i==60: aw_lineup_detected=True
            pbp_dataframe.at[i, 'AWAY_ONCOURT']=aw_foundplayers.copy()
            j=i
            while (not hm_lineup_detected):
                j+=1
                if pbp_dataframe.loc[j,'EVENTMSGTYPE']==8 and pbp_dataframe.loc[j,'PLAYER1_TEAM_ID']==game_info[1]:
                    if pbp_dataframe.loc[j,'PLAYER1_NAME'] not in hm_foundplayers:
                        hm_foundplayers.append(pbp_dataframe.loc[j,'PLAYER1_NAME'])
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

                # print("Known Bench")
                # print(hm_known_bench)
                # print("Found Players")
                # print(hm_foundplayers)
                if j-i==60: hm_lineup_detected=True
            pbp_dataframe.at[i, 'HOME_ONCOURT']=hm_foundplayers.copy()








def pull_pbp_date(extractdate,team_info_path,pbpoutput_path):
    team_info = game_info_scrap.load_team_info(team_info_path)
    games_list=game_info_scrap.scrap_scoreboard(extractdate,team_info)
    #[Game id, home id, home tri, away team id, away tricode]
    time.sleep(1)
    for i in games_list:
        tms_box=time.time()
        box_traditional=scrape_box_starter(i[0],'traditional')
        tme_box=time.time()
        print("Box Extract Time: "+ str(tme_box-tms_box))
        box_traditional.to_csv(pbpoutput_path+"box_trad_"+str(i[0])+"_"+str(i[2])+str(i[4])+".csv",index=False,na_rep="",float_format='%.0f')
        time.sleep(1)
        gamestarters=box_traditional.loc[box_traditional['START_POSITION']!="",['PLAYER_ID','PLAYER_NAME','TEAM_ID']]
        # print(gamestarters)

        tms_pbp=time.time()
        gamepbp=scrape_pbp(i[0],gamestarters,i)
        tme_pbp=time.time()
        print("PBP Extract Time: "+str(tme_pbp-tms_pbp))
        gamepbp.to_csv(pbpoutput_path+"pbp_"+str(i[0])+"_"+str(i[2])+str(i[4])+".csv",index=False,na_rep="",float_format='%.0f')
        time.sleep(2)

if __name__ == "__main__":
    # url1="http://data.nba.com/10s//prod/v2/20171027/scoreboard.json"
    global team_info
    pbpoutput=sys.argv[2]

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


    pull_pbp_date("10/17/2017",team_info_path,pbpoutput)
    # test_shot_scrap=scrape_shot_data("0021700002","201939","1610612744")
    # test_shot_scrap.to_csv(pbpoutput+"shots_sample_steph.csv",index=False,na_rep="")