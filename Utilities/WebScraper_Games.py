import requests 
import datetime
import json
from pymongo import MongoClient

client = MongoClient(port=27017)
db=client.nhl
games = db.games
stats = db.statlines


headers = {
  'authority': 'api.nhle.com',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
  'sec-ch-ua-platform': '"macOS"',
  'accept': '*/*',
  'origin': 'https://www.nhl.com',
  'sec-fetch-site': 'cross-site',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.nhl.com/',
  'accept-language': 'en-US,en;q=0.9'
}
i = 0
startDate = '20212022'
endDate = '20212022'
reports =("summary", "faceoffpercentages", "goalsbyperiod", "goalsforbystrength",
"realtime", "penalties", "powerplay", "powerplaytime", "summaryshooting", "percentages")

for report in reports:
    print(report)
    start = 0
    endCount = 1000
    while start < endCount:
        url = "https://api.nhle.com/stats/rest/en/team/"
        url += report
        url += "?isAggregate=false&isGame=true&sort=%5B%7B%22property%22:%22gameDate%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start="
        url += str(start)
        url += "&limit=100&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C="
        url += endDate
        url += "%20and%20seasonId%3E="
        url += startDate
        response = requests.get(url, headers=headers)
        gamedata = response.json()
        statlines = gamedata['data']
        endCount = gamedata['total']
        for statline in statlines:
            gameId = statline["gameId"]
            teamId = statline["teamId"]
            filter = {"gameId": gameId, "teamId": teamId}
            line = stats.find_one(filter)
            if line == None:
                stats.insert_one(statline)
            else:
                del statline["gameDate"]
                del statline["gameId"]
                values = {"$set": statline}
                stats.update_one(filter, values)
            filter = {"gameId": gameId}
            game = games.find_one(filter)
            homeRoad = statline["homeRoad"]
            if game == None:
                if homeRoad == "H":
                    values = {"gameId": gameId, "homeTeamId": teamId}
                else:
                    values = {"gameId": gameId, "awayTeamId": teamId}
                games.insert_one(values)
            else:
                if homeRoad == "H":
                    values = {"$set": {"homeTeamId": teamId}}
                else:
                    values = {"$set": {"awayTeamId": teamId}}
                games.update_one(filter, values)
        print(start)
        start += 100

print("Adding statlines to games...")
start_date = datetime.datetime(2021, 9, 1)
end_date = datetime.datetime(2022, 5, 16)
cursor = stats.find({"gameDate":{'$gte': start_date, '$lt': end_date}})
for statline in cursor:
    gameId = statline["gameId"]
    homeRoad = statline["homeRoad"]
    if homeRoad == "H":
        values = {"$set": {"homeStats": statline}}
    else:
        values = {"$set": {"awayStats": statline}}
    games.update_one({"gameId": gameId}, values)
print("Done")