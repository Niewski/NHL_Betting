import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import Mongo
import datetime
import Predictor
from sklearn.linear_model import LinearRegression

def getSeasonDates(season):
    seasonStr = str(season)
    yearBegin = int(seasonStr[0:4])
    yearEnd = int(seasonStr[4:]) 
    start = datetime.datetime(yearBegin, 9, 1)
    end = datetime.datetime(yearEnd, 5, 16)
    endLast = datetime.datetime(yearBegin, 2, 1)
    return (start, end, endLast)

yHome = []
yAway = []
xHome = []
xAway = []
leagueCursor = Mongo.getCursor("leagueaverages", {"seasonId":{"$gte": 20192020}})
leagueCursor.sort("seasonId", 1)
for season in leagueCursor:
    seasonId = season["seasonId"]
    print(seasonId)
    dates = getSeasonDates(seasonId)
    gamesCursor = Mongo.getCursor("games", {"gameDate":{"$gte": dates[0], "$lt": dates[1]}})
    for game in gamesCursor:
        homeId = game["homeTeamId"]
        awayId = game["awayTeamId"]
        homeScore = game["homeStats"]["goalsFor"]
        awayScore = game["awayStats"]["goalsFor"]
        gameDate = game["gameDate"]
        homeCursor = Mongo.getCursor("games", {"homeTeamId": homeId, "gameDate":{'$gte': dates[2], "$lt": gameDate}, "homeStats.satPct":{"$gte": 0}, "homeStats.shootingPct5v5":{"$gte": 0}, "homeStats.savePct5v5":{"$gte": 0}})
        homeCursor.sort("gameDate", -1)
        home = Predictor.get10GameAverages(homeCursor, "H")
        awayCursor = Mongo.getCursor("games", {"awayTeamId": awayId, "gameDate":{'$gte': dates[2], "$lt": gameDate}, "awayStats.satPct":{"$gte": 0}, "awayStats.shootingPct5v5":{"$gte": 0}, "awayStats.savePct5v5":{"$gte": 0}})
        awayCursor.sort("gameDate", -1)
        away = Predictor.get10GameAverages(awayCursor, "A")
        avgSF = season["shotsForPerGame"]
        avgSA = season["shotsAgainstPerGame"]
        avgCors = season["satPct"]
        avgGoalEff = season["shootingPct5v5"]
        avgSave = season["savePct5v5"]
        homeSF = home["shotsForPerGame"] / avgSF
        homeSA = home["shotsAgainstPerGame"] / avgSA
        homeCors = home["satPct"] / avgCors
        homeGoalEff = home["shootingPct5v5"] / avgGoalEff
        homeSave = home["savePct5v5"] / avgSave
        awaySF = away["shotsForPerGame"] / avgSF
        awaySA = away["shotsAgainstPerGame"] / avgSA
        awayCors = away["satPct"] / avgCors
        awayGoalEff = away["shootingPct5v5"] / avgGoalEff
        awaySave = away["savePct5v5"] / avgSave
        yHome.append([homeScore])
        yAway.append([awayScore])
        xH = np.empty(5)
        xA = np.empty(5)
        xH[0] = (homeSF - awaySF) * 100 
        xA[0] = (awaySF - homeSF) * 100
        xH[1] = (homeSA - awaySA) * 100  
        xA[1] = (awaySA - homeSA) * 100 
        xH[2] = (homeCors - awayCors) * 100 
        xA[2] = (awayCors - homeCors) * 100 
        xH[3] = (homeGoalEff - awayGoalEff) * 100  
        xA[3] = (awayGoalEff - homeGoalEff) * 100 
        xH[4] = (homeSave - awaySave) * 100 
        xA[4] = (awaySave - homeSave) * 100 
        xHome.append([xH])
        xAway.append([xA])
    
yHomeArr = np.asarray(yHome)
yAwayArr = np.asarray(yAway)
xHomeArr = np.asarray(xHome).reshape(-1, 5)
xAwayArr = np.asarray(xAway).reshape(-1, 5)
homeModel = LinearRegression().fit(xHomeArr, yHomeArr) 
awayModel = LinearRegression().fit(xAwayArr, yAwayArr) 
print("Home------------------------------")
print(homeModel.score(xHomeArr, yHomeArr))
print("Away------------------------------")
print(awayModel.score(xAwayArr, yAwayArr))
        
