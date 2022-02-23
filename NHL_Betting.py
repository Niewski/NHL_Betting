import numpy as np
import datetime
import Mongo
import DataModeler
import Predictor
import Kelly

today = [(14, 1.45, 22, 2.85), (8, 1.9, 7, 1.9), (17, 3.35, 21, 1.35), (25, 1.64, 52, 2.35), (53, 2.85, 26, 1.45)]
team_map = Mongo.getTeamMapping(20212022)
size = len(team_map)
x = np.empty((size + 1))
ratings = Mongo.getTeamRatings(20212022)
i = 0
while i < size:
    x[i] = ratings[i]
    i += 1
for game in today:
    prediction = Predictor.getForecastFromRatings(team_map, (game[0], game[2]), x)
    print(game, " : PR Prediction", round(prediction, 2))
    monte = Predictor.getMonteExpectations((game[0], game[2]), 20212022)
    arr = np.sum(monte, axis=0)
    homeWins = arr[0]
    homeGoals = arr[1]
    awayGoals = arr[2]
    draws = arr[3]
    homePercent = homeWins / 10000
    awayPercent = 1 - homePercent
    drawPercent = draws / 10000
    homeKelly = Kelly.getKellyDiff(homePercent, game[1], 5.0)
    awayKelly = Kelly.getKellyDiff(awayPercent, game[3], 5.0)
    homePercent = homePercent * 100
    awayPercent = awayPercent * 100
    drawPercent = drawPercent * 100
    homeAvg = homeGoals / 10000
    awayAvg = awayGoals / 10000
    avgGoals = homeAvg + awayAvg
    Predictor.getPoissonExpectations(homeAvg, awayAvg)
    print("Monte Carlo Estimates-----------------------")
    print("Home% :", round(homePercent, 2), " Odds:", round((100 / homePercent), 2))
    print("Away% :", round(awayPercent, 2), " Odds:", round((100 / awayPercent), 2))
    print("Draw% :", round(drawPercent, 2), " Odds:", round((100 / drawPercent), 2))
    print("Goals H | A : ", round(homeAvg, 2), "|", round(awayAvg, 2))
    print("Total Goals :", round(avgGoals, 2))
    print("Home Kelly :", homeKelly)
    print("Away Kelly :", awayKelly)
    print("--------------------------------------------")

def getGameStats(game):
    homeStats = game["homeStats"]
    awayStats = game["awayStats"]
    homeId = homeStats["teamId"]
    awayId = awayStats["teamId"]
    homeGoals = homeStats["goalsFor"]
    awayGoals = awayStats["goalsFor"]
    result = (homeId, awayId, (homeGoals - awayGoals))
    return result

def testPredictions():
    season = 20212022
    start_date = datetime.datetime(2021, 9, 1)
    end_date = datetime.datetime(2022, 5, 16)
    team_map = Mongo.getTeamMapping(season)
    size = len(team_map)
    x = np.empty((size + 1))
    ratings = Mongo.getTeamRatings(season);
    i = 0
    while i < size:
        x[i] = ratings[i]
        i += 1
    cursor = Mongo.getCursor("games", {"gameDate":{'$gte': start_date, '$lt': end_date}})
    realList = []
    predList = []
    for game in cursor:
        stats = getGameStats(game)
        realMargin = stats[2]
        prediction = Predictor.getForecastFromRatings(team_map, (stats[0], stats[1]), x)
        realList += [realMargin]
        predList += [prediction]
    Predictor.getAccuracyFromRatings(realList, predList)