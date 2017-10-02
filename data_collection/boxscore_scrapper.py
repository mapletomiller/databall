import sys
import urllib3
import bs4
import requests

def extract_boxscore(date,hometeam,awayteam,team_pull,box_type):
    players_box={}
    url="https://www.basketball-reference.com/boxscores/"+date+"0"+hometeam+".html"
    print(url)
    response = requests.get(url)
    html = response.content

    soup = bs4.BeautifulSoup(html)
    if team_pull=="home":
        team_box=hometeam.lower()
    boxpull="box_"+team_box+"_"+box_type
    table = soup.find('table', attrs={"id": boxpull})
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

    return players_box;
def stat_to_csv_writer(stats,outputfile):
    #Write the output

    return;
if __name__ == "__main__":
    ###
    players_box={}
    stat_categories=set()
    #Code here
    url="https://www.basketball-reference.com/boxscores/201706120GSW.html"
    response = requests.get(url)
    html = response.content

    soup = bs4.BeautifulSoup(html)
    table=soup.find('table',attrs={"id":"box_cle_basic"})
    #print(table.prettify())
    for row in table.findAll("tr"):
        for cell in row.findAll("th"):
            #print(cell)
            text=cell.text.replace('&nbsp;', '')
            rowtype=cell.get('data-stat')
            #print(rowtype)
            if rowtype=="player":
                playername=cell.get('csk')
                if playername not in players_box:
                    players_box[playername]={}
        #print("#######################")
        for elem in row.findAll("td"):
            text=elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players_box[playername][elemtype]=text
                stat_categories.add(elemtype)

        #print(row)
        #print("#######################")


    gsw_test=extract_boxscore("20170612","GSW","CLE","home","basic")
    for i in gsw_test:
        print(i)
        for j in gsw_test[i]:
            print(j+": "+str(gsw_test[i][j]))