from pymongo import MongoClient

client = MongoClient(port=27017)
db=client.nhl

def getCollection(x):
    if x == "games":
        collection = db.games
    elif x == "leagueaverages":
        collection = db.leagueaverages
    elif x == "teamaverages":
        collection = db.seasonaverages
    elif x == "statlines":
        collection = db.statlines
    elif x == "teams":
        collection = db.teams
    else:
        return None
    return collection

def getCursor(coll, filter):
    collection = getCollection(coll)
    cursor = collection.find(filter)
    return cursor

def getDocument(coll, filter):
    collection = getCollection(coll)
    cursor = collection.find_one(filter)
    return cursor

def addStatlines():
    statlines = db.statlines 
    games = db.games
    cursor = statlines.find({})
    for line in cursor:
        gameId = line["gameId"]
        homeRoad = line["homeRoad"]
        filter = {"gameId": gameId}
        if homeRoad == "H":
            values = {"$set":{"homeStats": line}}
        else:
            values = {"$set":{"awayStats": line}}
        games.update_one(filter, values)
    print("Done")

def getTeamMapping(seasonId):
    collection = getCollection("teamaverages")
    filter = {"seasonId": seasonId}
    cursor = collection.find(filter).sort("teamId", 1)
    map = {}
    i = 1
    for team in cursor:
        teamId = team["teamId"]
        map[teamId] = i
        i += 1
    return map

def setPowerRatings(seasonId, values):
    teams = getCollection("teamaverages")
    leagues = getCollection("leagueaverages")
    filter = {"seasonId": seasonId}
    homeAdv = values[0]
    value = {"$set":{"homeAdv": homeAdv}}
    league = leagues.find_one_and_update(filter, value)
    i = 1
    cursor = teams.find(filter).sort("teamId", 1)
    for team in cursor:
        teamId = team["teamId"]
        rating = values[i]
        filter = {"seasonId": seasonId, "teamId": teamId}
        value = {"$set":{"powerRating": rating}}
        teams.update_one(filter, value)
        i += 1

def setTeamRatings(seasonId, values):
    collection = getCollection("teamaverages")
    filter = {"seasonId": seasonId}
    cursor = collection.find(filter).sort("points", -1)
    i = 0
    for team in cursor:
        teamId = team["teamId"]
        rating = values[i]
        filter = {"seasonId": seasonId, "teamId": teamId}
        value = {"$set":{"powerRating": rating}}
        collection.update_one(filter, value)
        i += 1
    
def getTeamRatings(seasonId):
    collection = getCollection("teamaverages")
    leagues = getCollection("leagueaverages")
    filter = {"seasonId": seasonId}
    league = leagues.find_one(filter)
    cursor = collection.find(filter).sort("teamId", 1)
    ratings = {}
    ratings[0] = league["homeAdv"]
    i = 1
    for team in cursor:
        ratings[i] = team["powerRating"]
        i += 1
    return ratings