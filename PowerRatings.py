import sys
import numpy as np
import datetime
import Mongo
from scipy import optimize

def setInitialRatings():
    Mongo.setTeamRatings(season, initial_ratings)
    print("Ratings Initialized.")

season = 20212022
start_date = datetime.datetime(2021, 9, 1)
end_date = datetime.datetime(2022, 5, 16)
home_adv = 0.3
initial_ratings = (1.5, 1.4, 1.3, 1.2, 1.1, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9, -1, -1.1, -1.2, -1.3, -1.4, -1.5, -1.6)
#setInitialRatings()
team_map = Mongo.getTeamMapping(season)
size = len(team_map)
x = np.empty((size + 1))
ratings = Mongo.getTeamRatings(season);
i = 0
while i < size:
    x[i] = ratings[i]
    i += 1

def setPowerRatings():
    cons = { 'type':'eq', 'fun': MeanOfArray }
    bnds = [(-3, 3)]
    i = 0
    while i < size:
        bnds += [(-10, 10)]
        i += 1
    result = optimize.minimize(SumOfSquares, x0 = x, bounds=bnds, constraints = cons)
    print(result)
    results = result.x
    Mongo.setPowerRatings(season, results)
    print("Done")

def MeanOfArray(x):
    size = x.size
    newX = np.empty((size-1))
    i = 1
    while i < size:
        newX[i-1] = x[i]
        i += 1
    return np.mean(newX)

def SumOfSquares(x):
    cursor = Mongo.getCursor("games", {"gameDate":{'$gte': start_date, '$lt': end_date}})
    sumError = 0
    for game in cursor:
        error = getSquaredError(game, x)
        if sumError > (sys.float_info.max - error):
            sumError = sys.float_info.max
        else:
            sumError += error
    return sumError

def getSquaredError(game, x):
    homeStats = game["homeStats"]
    awayStats = game["awayStats"]
    homeId = homeStats["teamId"]
    awayId = awayStats["teamId"]
    homeGoals = homeStats["goalsFor"]
    awayGoals = awayStats["goalsFor"]
    realMargin = homeGoals - awayGoals
    predictedMargin = getForecast(homeId, awayId, x)
    error = (realMargin - predictedMargin) ** 2
    return error

def getForecast(homeId, awayId, x):
    home = team_map[homeId]
    away = team_map[awayId]
    homeAdv = x[0]
    homeRating = x[home]
    awayRating = x[away]
    return ((homeAdv + homeRating) - awayRating)

setPowerRatings()
setPowerRatings()