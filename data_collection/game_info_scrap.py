import os
import requests
import json
import sys

HEADERS = {
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

def scrap_scoreboard(extractdate):
    global HEADERS
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
    data = requests.get(url, timeout=5, headers=HEADERS).json()
    games=[]
    for i in data['resultSets'][0]['rowSet']:
        games.append([i[2],i[6],lookup_team_attribute(team_info,"tricode",str(i[6])),i[7],lookup_team_attribute(team_info,"tricode",str(i[7]))])

    return games;


if __name__ == "__main__":
    global HEADERS
    team_info_path=sys.argv[1]

    team_info=load_team_info(team_info_path)
    game_sample=scrap_scoreboard("11/04/2017")
    for i in game_sample: print(i)

