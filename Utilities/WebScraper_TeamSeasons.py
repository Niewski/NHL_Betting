import requests 
import datetime
import json
from pymongo import MongoClient

client = MongoClient(port=27017)
db=client.nhl
stats = db.seasonaverages


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
season = "20212022"
reports =("summary", "faceoffpercentages", "goalsbyperiod", "goalsforbystrength", "realtime",
"penalties", "powerplay", "powerplaytime", "summaryshooting", "percentages")

for report in reports:
    print(report)
    url = "https://api.nhle.com/stats/rest/en/team/"
    url += report
    url += "?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22teamFullName%22,%22direction%22:%22ASC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=100&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C="
    url += season
    url += "%20and%20seasonId%3E="
    url += season
    response = requests.get(url, headers=headers)
    seasondata = response.json()
    teamaverages = seasondata['data']
    for teamaverage in teamaverages:
        seasonId = teamaverage["seasonId"]
        teamId = teamaverage["teamId"]
        filter = {"seasonId": seasonId, "teamId": teamId}
        line = stats.find_one(filter)
        if line == None:
            print("Missed one")
        else:
            values = {"$set": teamaverage}
            stats.update_one(filter, values)

