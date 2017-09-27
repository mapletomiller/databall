import sys
import urllib3
import bs4
import requests

def extract_boxscore(date,hometeam,awayteam):
    stats={}
    return stats;

if __name__ == "__main__":
    ###
    players={}
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
                if playername not in players:
                    players[playername]={}
        #print("#######################")
        for elem in row.findAll("td"):
            text=elem.text.replace('&nbsp;', '')
            elemtype = elem.get('data-stat')
            if elemtype != "reason":
                players[playername][elemtype]=text

        #print(row)
        #print("#######################")
    for i in players:
        print(i)
        for j in players[i]:
            print(j+": "+str(players[i][j]))