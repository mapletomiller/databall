import sys
import urllib3
import bs4
import requests
import calendar
import time


def load_schedule(month,extract_day):
    global team_abrvs
    with open(month+"_sched.csv",'r') as monthschedule:
        next(monthschedule)
        games=[]
        for line in monthschedule:
            hometeam=line.split(",")[4].strip()
            awayteam=line.split(",")[2].strip()
            datefull=line.split(",")[0].strip()
            datefinal=str(datefull.split(" ")[3])+str(month_abrvs[datefull.split(" ")[1]])+str(datefull.split(" ")[2])
            hometeam_abr=team_abrvs[hometeam]
            awayteam_abr=team_abrvs[awayteam]
            #print(datefinal+"|"+hometeam_abr+"|"+awayteam_abr)
            if datefinal==extract_day:
                games.append((datefinal,hometeam_abr,awayteam_abr))
    return games;
def extract_boxscore(date,hometeam,awayteam):
    players_box={}
    url="https://www.basketball-reference.com/boxscores/"+date+"0"+hometeam+".html"
    # print(url)
    response = requests.get(url)
    html = response.content

    soup = bs4.BeautifulSoup(html)
    home_team_box=hometeam.lower()
    away_team_box=awayteam.lower()
    boxpull_basic="box_"+home_team_box+"_basic"
    table = soup.find('table', attrs={"id": boxpull_basic})
    # print(table.prettify())
    for row in table.findAll("tr"):
        for cell in row.findAll("th"):
            # print(cell)
            text = cell.text.replace('&nbsp;', '')
            rowtype = cell.get('data-stat')
            # print(rowtype)
            if rowtype == "player":
                playername = cell.get('csk')
                if playername not in players_box:
                    players_box[playername] = {}
        # print("#######################")
        for elem in row.findAll("td"):
            text = elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players_box[playername][elemtype] = text
    boxpull_adv="box_"+home_team_box+"_advanced"
    table = soup.find('table', attrs={"id": boxpull_adv})
    # print(table.prettify())
    for row in table.findAll("tr"):
        for cell in row.findAll("th"):
            # print(cell)
            text = cell.text.replace('&nbsp;', '')
            rowtype = cell.get('data-stat')
            # print(rowtype)
            if rowtype == "player":
                playername = cell.get('csk')
                if playername not in players_box:
                    players_box[playername] = {}
        # print("#######################")
        for elem in row.findAll("td"):
            text = elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players_box[playername][elemtype] = text
    all_stat=[players_box]
    players_box={}
    ###AWAY TEAM
    boxpull_basic = "box_" + away_team_box + "_basic"
    table = soup.find('table', attrs={"id": boxpull_basic})
    # print(table.prettify())
    for row in table.findAll("tr"):
        for cell in row.findAll("th"):
            # print(cell)
            text = cell.text.replace('&nbsp;', '')
            rowtype = cell.get('data-stat')
            # print(rowtype)
            if rowtype == "player":
                playername = cell.get('csk')
                if playername not in players_box:
                    players_box[playername] = {}
        # print("#######################")
        for elem in row.findAll("td"):
            text = elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players_box[playername][elemtype] = text
    boxpull_adv = "box_" + away_team_box + "_advanced"
    table = soup.find('table', attrs={"id": boxpull_adv})
    # print(table.prettify())
    for row in table.findAll("tr"):
        for cell in row.findAll("th"):
            # print(cell)
            text = cell.text.replace('&nbsp;', '')
            rowtype = cell.get('data-stat')
            # print(rowtype)
            if rowtype == "player":
                playername = cell.get('csk')
                if playername not in players_box:
                    players_box[playername] = {}
        # print("#######################")
        for elem in row.findAll("td"):
            text = elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players_box[playername][elemtype] = text
    all_stat.append(players_box)
    return all_stat;
def stat_to_csv_writer(stats,outputfile,date,team):
    #Write the output
    global stat_categories
    with open(outputfile,"w") as outwrite:
        headerline="player_name|date|team"
        for statname in stat_categories["basic"]:
            headerline+="|"+statname
        for statname in stat_categories["advanced"]:
            headerline+="|"+statname
        outwrite.write(headerline+"\n")
        for player in stats:
            #print(player)
            if player != None:
                outline=player+"|"+date+"|"+team
                for statcat in stat_categories["basic"]:
                    if statcat in stats[player]:
                        outline+="|"+str(stats[player][statcat])
                    else:
                        outline+="|NA"
                for statcat in stat_categories["advanced"]:
                    if statcat in stats[player]:
                        outline+="|"+str(stats[player][statcat])
                    else:
                        outline+="|NA"
                outwrite.write(outline+"\n")

    return;
if __name__ == "__main__":
    ###
    ###INIT VARS ###
    outputpath=sys.argv[1]
    extract_day=sys.argv[2]
    players_box={}
    stat_categories={"advanced":['efg_pct','ts_pct','fg3a_per_fga_pct','fta_per_fga_pct','orb_pct','drb_pct','trb_pct','ast_pct','stl_pct','blk_pct','tov_pct','off_rtg','def_rtg','usg_pct'],"basic":['mp','fg','fga','fg_pct','fg3','fg3a','fg3_pct','ft','fta','ft_pct','pts','drb','orb','trb','ast','stl','blk','tov','pf']}
    month_abrvs={v: k for k,v in enumerate(calendar.month_abbr)}
    team_abrvs = {}
    with open("Team_abrevs.csv",'r') as abrvs_file:
        for line in abrvs_file:
            team_abrvs[line.split(',')[0].strip()]=str(line.split(',')[1].strip())

    #Code here
    #url="https://www.basketball-reference.com/boxscores/201706120GSW.html"
    #response = requests.get(url)
    #html = response.content

    #soup = bs4.BeautifulSoup(html)
    #table=soup.find('table',attrs={"id":"box_cle_basic"})
    #print(table.prettify())
    #for row in table.findAll("tr"):
    #    for cell in row.findAll("th"):
    #        #print(cell)
    #        text=cell.text.replace('&nbsp;', '')
    #        rowtype=cell.get('data-stat')
    #        #print(rowtype)
    #        if rowtype=="player":
    #            playername=cell.get('csk')
    #            if playername not in players_box:
    #                players_box[playername]={}
        #print("#######################")
     #   for elem in row.findAll("td"):
     #       text=elem.text.replace('&nbsp;', '')
     #       elemtype = elem.get('data-stat')
     #       if elemtype != "reason":
     #           players_box[playername][elemtype]=text


        #print(row)
        #print("#######################")

    extract_games=load_schedule("oct",extract_day)
    for ind_game in extract_games:
        game_data=extract_boxscore(extract_day,ind_game[1],ind_game[2])
        print(extract_day+"|"+ind_game[1]+"|"+ind_game[2])
        time.sleep(2)
        stat_to_csv_writer(game_data[0],outputpath+"/"+extract_day+ind_game[1]+".txt",extract_day,ind_game[1])
        stat_to_csv_writer(game_data[1], outputpath + "/" + extract_day + ind_game[2] + ".txt", extract_day,ind_game[2])

    # gsw_test=extract_boxscore("20171017","GSW","HOU","home","advanced")
    # stat_to_csv_writer(gsw_test,outputpath+"/20171017GSW.txt","20171017","GSW")
    # for i in gsw_test:
    #    print(i)
    #    for j in gsw_test[i]:
    #        print(j+": "+str(gsw_test[i][j]))