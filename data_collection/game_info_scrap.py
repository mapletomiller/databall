import os
import requests
import json
import sys
import time

global api_headers
api_headers = {
    'origin': ('http://stats.nba.com'),
    'user-agent': (
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'),
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en')

}

def load_team_info(filepath):
    team_info=[]
    with open (filepath) as datafile:
        alldata=json.load(datafile)
    for i in alldata['league']['standard']:
        team_info.append(i)
    return team_info;

def lookup_team_attribute(team_info_list,attribute,team_id):
    # isNBAFranchise: true,
    # isAllStar: false,
    # city: "Atlanta",
    # altCityName: "Atlanta",
    # fullName: "Atlanta Hawks",
    # tricode: "ATL",
    # teamId: "1610612737",
    # nickname: "Hawks",
    # urlName: "hawks",
    # confName: "East",
    # divName: "Southeast"

    x='Not Found'
    for i in team_info_list:
        if i['teamId']==team_id:
            x=i[attribute]
    return x;
def scrap_team_standings():
    return 0;

def scrap_scoreboard(extractdate,team_info):
    global api_headers
    # headers: [
    #     "GAME_DATE_EST",
    #     "GAME_SEQUENCE",
    #     "GAME_ID",
    #     "GAME_STATUS_ID",
    #     "GAME_STATUS_TEXT",
    #     "GAMECODE",
    #     "HOME_TEAM_ID",
    #     "VISITOR_TEAM_ID",
    #     "SEASON",
    #     "LIVE_PERIOD",
    #     "LIVE_PC_TIME",
    #     "NATL_TV_BROADCASTER_ABBREVIATION",
    #     "HOME_TV_BROADCASTER_ABBREVIATION",
    #     "AWAY_TV_BROADCASTER_ABBREVIATION",
    #     "LIVE_PERIOD_TIME_BCAST",
    #     "ARENA_NAME",
    #     "WH_STATUS"
    # ],

    url="http://stats.nba.com/stats/scoreboardv2/?leagueId=00&gameDate={datepull}&dayOffset=0".format(datepull=extractdate)
    data = requests.get(url, timeout=15, headers=api_headers).json()
    games=[]
    for i in data['resultSets'][0]['rowSet']:
        gamedate = i[0][0:10]
        games.append([i[2],i[6],lookup_team_attribute(team_info,"tricode",str(i[6])),i[7],lookup_team_attribute(team_info,"tricode",str(i[7])),gamedate])

    return games;

def scrap_box_trad(gameid):

    url = "http://stats.nba.com/stats/boxscoretraditionalv2/?gameId={gID}&startPeriod=0&endPeriod=14&startRange=0&endRange=2147483647&rangeType=0".format(gID=gameid)
    data = requests.get(url, timeout=5, headers=api_headers).json()
    gamedata={"gameid":gameid,'players':[]}
    dataheaders=data['resultSets'][0]['rowSet']
    # headers: [
    #     "GAME_ID",
    #     "TEAM_ID",
    #     "TEAM_ABBREVIATION",
    #     "TEAM_CITY",
    #     "PLAYER_ID",
    #     "PLAYER_NAME",
    #     "START_POSITION",
    #     "COMMENT",
    #     "MIN",
    #     "FGM",
    #     "FGA",
    #     "FG_PCT",
    #     "FG3M",
    #     "FG3A",
    #     "FG3_PCT",
    #     "FTM",
    #     "FTA",
    #     "FT_PCT",
    #     "OREB",
    #     "DREB",
    #     "REB",
    #     "AST",
    #     "STL",
    #     "BLK",
    #     "TO",
    #     "PF",
    #     "PTS",
    #     "PLUS_MINUS"
    # ],
    for i in data['resultSets'][0]['rowSet']:
        gamedata['players'].append({'player_name':i[5],
                                    'player_id':i[4],
                                    'starter':i[6]
                                    })
    return gamedata;

if __name__ == "__main__":
    team_info_path=sys.argv[1]

    team_info=load_team_info(team_info_path)
    game_sample=scrap_scoreboard("10/17/2017")
    for i in game_sample:
        time.sleep(2)
        sample_game_box=scrap_box_trad(i[0])
    # print(sample_game_box)

