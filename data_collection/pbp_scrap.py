import urllib3
import json
import codecs
import requests

def scrape_pbp(game_id):
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

    return 0;

def load_player_info(inputpath):
    player_dict={}

    return player_dict;

def description_parser(description_text):
    x=('who,what,when')

    return x;


if __name__ == "__main__":
    url1="http://data.nba.com/10s//prod/v2/20171027/scoreboard.json"

# reader = codecs.getreader("utf-8")
# http=urllib3.PoolManager()
# data=json.load(reader(http.urlopen("GET",url1)))
    data=requests.get(url1).json()
    print(data['games'][0]['gameId'])
    for i in data['games']:
        print(i['gameId'])
        print(i['vTeam']['triCode'])
        print(i['hTeam']['triCode'])