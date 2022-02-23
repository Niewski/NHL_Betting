import requests 
import datetime
from pymongo import MongoClient

client = MongoClient(port=27017)
db=client.nhl
teams = db.teams
cursor = teams.find({})
team_map = {}
for team in cursor:
    team_id = team["teamId"]
    abb = team["abb"]
    team_map[abb] = team_id

parameters = {
    "key": "92d40f583da946db8740b7d5ae97624d"
}
response = requests.get("https://api.sportsdata.io/v3/nhl/scores/json/Games/2018", params=parameters)
entries = response.json()

games = db.games
for entry in entries:
    game = {}
    home_abb = entry["HomeTeam"]
    away_abb = entry["AwayTeam"]
    date = entry["Day"]
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    game["date"] = datetime.datetime(year, month, day)
    game["home_teamId"] = team_map[home_abb]
    game["away_teamId"] = team_map[away_abb]
    goals_home = entry["HomeTeamScore"]
    goals_away = entry["AwayTeamScore"]
    shots_home = "?"
    shots_away = "?"
    game["goals_home"] = goals_home
    game["goals_away"] = goals_away
    game["shots_home"] = shots_home
    game["shots_away"] = shots_away
    save_rate_home = "?"
    save_rate_away = "?"
    game["save_rate_home"] = save_rate_home
    game["save_rate_away"] = save_rate_away
    game["pp_fo_home"] = "?"
    game["pp_fow_home"]  = "?"
    game["pp_fo_away"] = "?"
    game["pp_fow_away"]  = "?"
    ev_fow_home  = "?"
    ev_fow_away  = "?"
    game["ev_fow_home"] = ev_fow_home
    game["ev_fow_away"] = ev_fow_away
    game["bks_home"]  = "?"
    game["bks_away"]  = "?"
    game["gva_home"]  = "?"
    game["gva_away"]  = "?"
    game["tka_home"]  = "?"
    game["tka_away"]  = "?"
    game["pp_opp_home"]  = "?"
    game["pp_opp_away"]  = "?"
    game["pp_goals_home"]  = "?"
    game["pp_goals_away"]  = "?"
    game["sh_goals_home"]  = "?"
    game["sh_goals_away"]  = "?"
    games.insert_one(game).inserted_id

print("done)")