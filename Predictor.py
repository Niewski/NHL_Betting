import numpy as np
import Mongo
import datetime
from sklearn.linear_model import LinearRegression
from scipy import stats

def getMonteExpectations(ids, season):
    start_date = datetime.datetime(2021, 9, 1)
    league = Mongo.getDocument("leagueaverages", {"seasonId": season})
    homeCursor = Mongo.getCursor("games", {"homeTeamId": ids[0], "gameDate":{'$gte': start_date}, "homeStats.satPct":{"$gte": 0}})
    homeCursor.sort("gameDate", -1)
    awayCursor = Mongo.getCursor("games", {"awayTeamId": ids[1], "gameDate":{'$gte': start_date}, "awayStats.satPct":{"$gte": 0}})
    awayCursor.sort("gameDate", -1)
    home = get10GameAverages(homeCursor, "H")
    away = get10GameAverages(awayCursor, "A")
    homeDoc = Mongo.getDocument("teamaverages", {"teamId": ids[0], "seasonId": season})
    awayDoc = Mongo.getDocument("teamaverages", {"teamId": ids[1], "seasonId": season})
    home["powerRating"] = homeDoc["powerRating"]
    away["powerRating"] = awayDoc["powerRating"]
    results = np.empty([10000, 4])
    i = 0
    while i < 10000:    
        result = basicMonteCarlo(league, home, away)
        results[i] = result
        i += 1
    return results

def get10GameAverages(cursor, homeRoad):
    stats = np.empty([10, 8])
    i = 0
    for game in cursor:
        if homeRoad == "H":
            statline = game["homeStats"]
        else:
            statline = game["awayStats"]
        if i < 10:
            stats[i,0] = statline["shotsForPerGame"]
            stats[i,1] = statline["shotsAgainstPerGame"]
            stats[i,2] = statline["satPct"]
            stats[i,3] = statline["shootingPct5v5"]
            stats[i,4] = statline["savePct5v5"]
            stats[i,5] = statline["shootingPlusSavePct5v5"]
            stats[i,6] = statline["evFaceoffPct"]
            stats[i,7] = statline["usatPct"]
        i += 1
    statAvg = np.mean(stats, axis=0)
    statDoc = {"shotsForPerGame": statAvg[0],
    "shotsAgainstPerGame": statAvg[1],
    "satPct": statAvg[2],
    "shootingPct5v5": statAvg[3],
    "savePct5v5": statAvg[4]}
    return statDoc

def basicMonteCarlo(league, home, away):
    avgSF = league["shotsForPerGame"]
    avgSA = league["shotsAgainstPerGame"]
    avgCors = league["satPct"]
    avgGoalEff = league["shootingPct5v5"]
    avgSave = league["savePct5v5"]
    homeSF = home["shotsForPerGame"] / avgSF
    homeSA = home["shotsAgainstPerGame"] / avgSA
    homeCors = home["satPct"] / avgCors
    homeGoalEff = home["shootingPct5v5"] / avgGoalEff
    homeSave = home["savePct5v5"] / avgSave
    homePR = home["powerRating"]
    awaySF = away["shotsForPerGame"] / avgSF
    awaySA = away["shotsAgainstPerGame"] / avgSA
    awayCors = away["satPct"] / avgCors
    awayGoalEff = away["shootingPct5v5"] / avgGoalEff
    awaySave = away["savePct5v5"] / avgSave
    awayPR = away["powerRating"]
    totalShots = (avgSF * (1 + homeSF - awaySA)) + (avgSF + (1 + awaySF - homeSA))
    homeShotChance = (0.5 + (homeCors - awayCors))
    awayShotChance = 1 - homeShotChance
    homeGoalChance = avgGoalEff * (1 + homeGoalEff - awaySave)
    awayGoalChance = avgGoalEff * (1 + awayGoalEff - homeSave)
    homeSaveChance = 1 - awayGoalChance
    awaySaveChance = 1 - homeGoalChance
    homeOTChance = (50 + (homePR - awayPR)) / 100
    awayOTChance = 1 - homeOTChance
    homeGoals = 0
    awayGoals = 0
    draw = 0
    i = 0
    while i < totalShots:
        nextShot = np.random.choice([1, 0], p=[homeShotChance, awayShotChance])
        if nextShot == 1:
            homeGoals += np.random.choice([1,0], p=[homeGoalChance, awaySaveChance])
        else:
            awayGoals += np.random.choice([1,0], p=[awayGoalChance, homeSaveChance])
        i += 1
    if homeGoals > awayGoals:
        winner = 1
    elif awayGoals > homeGoals:
        winner = 0
    else:
        draw = 1
        winner = np.random.choice([1,0], p=[homeOTChance, awayOTChance])
    return np.array([winner, homeGoals, awayGoals, draw])

def getForecastFromRatings(map, ids, x):
    home = map[ids[0]]
    away = map[ids[1]]
    homeAdv = x[0]
    homeRating = x[home]
    awayRating = x[away]
    return ((homeAdv + homeRating) - awayRating)

def getAccuracyFromRatings(real, predicted):
    i = 0
    correct = 0
    att = 0
    moneylines = 0
    threshold = 0.4
    for prediction in predicted:
        margin = real[i]
        spread = round(prediction)
        if prediction > threshold:
            att += 1
            if margin > 0:
                moneylines += 1
        elif prediction < (0 - threshold):
            att += 1
            if margin < 0:
                moneylines += 1
        if spread == margin:
            correct += 1
        i += 1
    accuracy = correct / i
    money_acc = moneylines / att
    print("Spread Bets: ", i)
    print("Spread Accuracy: ", accuracy * 100)
    print("Moneyline Bets Made: ", att)
    print("Moneylines: ", money_acc * 100)

def getPoissonExpectations(home, away):
    distHome = np.random.poisson(home, 10000)
    distAway = np.random.poisson(away, 10000)
    homeW = 0
    awayW = 0
    draw = 0
    i = 0
    while i < 10000:
        margin = distHome[i] - distAway[i]
        if margin > 0:
            homeW += 1
        elif margin < 0:
            awayW += 1
        else:
            draw += 1
            homeW += 0.5
            awayW += 0.5
        i += 1
    homePercent = round(homeW / 100, 2)
    awayPercent = round(awayW / 100, 2)
    drawPercent = round(draw / 100, 2)
    homeGoals = int(stats.mode(distHome)[0])
    awayGoals = int(stats.mode(distAway)[0])
    totalGoals = homeGoals + awayGoals
    print("Poisson Estimates----------------------------")
    print("Home% :", homePercent, " Odds:", round((100 / homePercent), 2))
    print("Away% :", awayPercent, " Odds:", round((100 / awayPercent), 2))
    print("Draw% :", drawPercent, " Odds:", round((100 / drawPercent), 2))
    print("Goals H | A : ", homeGoals, "|", awayGoals)
    print("Total Goals :", totalGoals)
