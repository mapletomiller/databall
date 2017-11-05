import sys
import urllib3
import bs4
import requests
import calendar
import time


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
def load_dfs_sal(datapath,day):
    global salaries
    with open(datapath+"/DKSalaries_"+day+".csv") as salary_data:
        for line in salary_data:

            player_pos=line.split(",")[0].strip('\"')
            player_name = line.split(",")[1].strip('\"')
            player_sal = line.split(",")[2].strip('\"')
            salaries[player_name]=[player_pos,player_sal]
    return;
def join_dfs_data(box_name,data_return):
    global salaries
    dfs_name=box_name.split(",")[1].strip()+" "+box_name.split(",")[0].strip()

    if dfs_name not in salaries:
        dfs_name_fixed = name_fixes(dfs_name)
        if dfs_name_fixed not in salaries:
            print(dfs_name+" Not Available")
            stat="NA"
        else:
            if data_return == "salary":
                stat = salaries[dfs_name_fixed][1]
            else:
                stat = salaries[dfs_name_fixed][0]
    else:
        if data_return=="salary":
            stat=salaries[dfs_name][1]
        else:
            stat=salaries[dfs_name][0]
    return stat;
def load_schedule(month,extract_day):
    global team_abrvs
    with open(month+"_sched.csv",'r') as monthschedule:
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
            if datefinal==extract_day:
                games.append((datefinal,hometeam_abr,awayteam_abr))
            team_sched[hometeam_abr].append(datefinal)
            team_sched[awayteam_abr].append(datefinal)
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
        headerline="player_name|date|game_index|team|dfs_salary|dfs_position"
        for statname in stat_categories["basic"]:
            headerline+="|"+statname
        for statname in stat_categories["advanced"]:
            headerline+="|"+statname
        outwrite.write(headerline+"\n")
        for player in stats:
            #print(player)
            if player != None:
                dfsal=join_dfs_data(player,"salary")
                dfspos=join_dfs_data(player,"position")
                outline=player+"|"+date+"|"+str(team_sched[team].index(extract_day)+1)+"|"+team+"|"+str(dfsal)+"|"+dfspos
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
    extract_day_start=int(sys.argv[2])
    extract_day_end=int(sys.argv[3])
    dfs_data_path=sys.argv[4]
    players_box={}
    team_sched={}
    salaries={}
    stat_categories={"advanced":['efg_pct','ts_pct','fg3a_per_fga_pct','fta_per_fga_pct','orb_pct','drb_pct','trb_pct','ast_pct','stl_pct','blk_pct','tov_pct','off_rtg','def_rtg','usg_pct'],"basic":['mp','fg','fga','fg_pct','fg3','fg3a','fg3_pct','ft','fta','ft_pct','pts','drb','orb','trb','ast','stl','blk','tov','pf','plus_minus']}
    month_abrvs={v: k for k,v in enumerate(calendar.month_abbr)}
    team_abrvs = {}
    with open("Team_abrevs.csv",'r') as abrvs_file:
        for line in abrvs_file:
            team_abrvs[line.split(',')[0].strip()]=str(line.split(',')[1].strip())
            team_sched[line.split(',')[1].strip()]=[]

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
    for i in range(extract_day_start,extract_day_end):
        extract_day=str(i)
        extract_games=load_schedule("full",extract_day)
        load_dfs_sal(dfs_data_path,extract_day[4:8])
        for ind_game in extract_games:
            game_data=extract_boxscore(extract_day,ind_game[1],ind_game[2])
            print(extract_day+"|"+ind_game[1]+"|"+ind_game[2]+"|"+str(team_sched[ind_game[1]].index(extract_day)+1))
            time.sleep(2)
            stat_to_csv_writer(game_data[0],outputpath+"/"+extract_day+ind_game[1]+".txt",extract_day,ind_game[1])
            stat_to_csv_writer(game_data[1], outputpath + "/" + extract_day + ind_game[2] + ".txt", extract_day,ind_game[2])

    # gsw_test=extract_boxscore("20171017","GSW","HOU","home","advanced")
    # stat_to_csv_writer(gsw_test,outputpath+"/20171017GSW.txt","20171017","GSW")
    # for i in gsw_test:
    #    print(i)
    #    for j in gsw_test[i]:
    #        print(j+": "+str(gsw_test[i][j]))