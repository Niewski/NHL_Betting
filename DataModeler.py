import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

def getArrays(cursor, count):
    y = np.empty([count], dtype=int)
    x_data = np.empty([count, 3])
    i = 0
    for game in cursor:
        goals_home = game["goals_home"]
        goals_away = game["goals_away"]
        shots_home = game["shots_home"]
        shots_away = game["shots_away"]
        ge_home = (goals_home / shots_home) * 100
        ge_away = (goals_away / shots_away) * 100
        y[i] = goals_home - goals_away
        x_data[i, 0] = game["save_rate_home"] - game["save_rate_away"]
        x_data[i, 1] = shots_home - shots_away
  #      x_data[i, 2] = game["ev_fow_home"] - game["ev_fow_away"]
        x_data[i, 2] = ge_home - ge_away
 #       ppo_home = game["pp_opp_home"]
  #      ppg_home = game["pp_goals_home"]
  #      ppo_away = game["pp_opp_away"]
  #      ppg_away = game["pp_goals_away"]
  #      pp_diff = 0
  #      if ppo_home > 0:
 #           if ppo_away > 0:
#                pp_diff = (ppg_home / ppo_home) - (ppg_away / ppo_away)
       # x_data[i, 4] = pp_diff
       # x_data[i, 5] = game["bks_home"] - game["bks_away"]
        i = i + 1
    x = x_data.reshape((-1, 3))
    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=True)
    return (x_train, x_test, y_train, y_test)

def getArraysForSpread(cursor, count):
    y = np.empty([count], dtype=int)
    x_data = np.empty([count, 2])
    i = 0
    for game in cursor:
        y[i] = game["goals_home"] - game["goals_away"]
        x_data[i, 0] = game["save_rate_home"] - game["save_rate_away"]
        x_data[i, 1] = game["shots_home"] - game["shots_away"]
        i = i + 1
    x = x_data.reshape((-1, 2))
    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=True)
    return (x_train, x_test, y_train, y_test)

def getAverageArrays(cursor, teams, count):
    y = np.empty([count], dtype=int)
    x_data = np.empty([count, 6])
    i = 0
    for game in cursor:
        y[i] = game["goals_home"] - game["goals_away"]
        home_id = game["home_teamId"] - 1
        away_id = game["away_teamId"] - 1
        home_rank = teams[home_id, 0]
        away_rank = teams[away_id, 0]
        if home_rank < 16:
            save_away = teams[away_id, 2]
            shots_away = teams[away_id, 5]
            ge_away = teams[away_id, 8]
            fow_away = teams[away_id, 11]
            pp_away = teams[away_id, 14]
            bks_away = teams[away_id, 17]
        else:
            save_away = teams[away_id, 2]
            shots_away = teams[away_id, 6]
            ge_away = teams[away_id, 9]
            fow_away = teams[away_id, 12]
            pp_away = teams[away_id, 15]
            bks_away = teams[away_id, 18]
        if away_rank < 16:
            save_home = teams[home_id, 2]
            shots_home = teams[home_id, 5]
            ge_home = teams[home_id, 8]
            fow_home = teams[home_id, 11]
            pp_home = teams[home_id, 14]
            bks_home = teams[home_id, 17]
        else:
            save_home = teams[home_id, 2]
            shots_home = teams[home_id, 6]
            ge_home = teams[home_id, 9]
            fow_home = teams[home_id, 12]
            pp_home = teams[home_id, 15]
            bks_home = teams[home_id, 18]
        x_data[i, 0] = save_home - save_away
        x_data[i, 1] = shots_home - shots_away
        x_data[i, 2] = fow_home - fow_away
        x_data[i, 2] = ge_home - ge_away
        x_data[i, 4] = pp_home - pp_away
        x_data[i, 5] = bks_home - bks_away
        i = i + 1
    x = x_data.reshape((-1, 6))
    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=False)
    return (x_train, x_test, y_train, y_test)

def getAverageArraysForFitting(cursor, teams, count):
    y = np.empty([count], dtype=int)
    x_data = np.empty([count, 6])
    i = 0
    for game in cursor:
        y[i] = game["goals_home"] - game["goals_away"]
        home_id = game["home_teamId"] - 1
        away_id = game["away_teamId"] - 1
        save_away = teams[away_id, 1]
        shots_away = teams[away_id, 4]
        ge_away = teams[away_id, 7]
        fow_away = teams[away_id, 10]
        pp_away = teams[away_id, 13]
        bks_away = teams[away_id, 16]
        save_home = teams[home_id, 1]
        shots_home = teams[home_id, 4]
        ge_home = teams[home_id, 7]
        fow_home = teams[home_id, 10]
        pp_home = teams[home_id, 13]
        bks_home = teams[home_id, 16]
        x_data[i, 0] = save_home - save_away
        x_data[i, 1] = shots_home - shots_away
        x_data[i, 2] = fow_home - fow_away
        x_data[i, 3] = ge_home - ge_away
        x_data[i, 4] = pp_home - pp_away
        x_data[i, 5] = bks_home - bks_away
        i = i + 1
    x = x_data.reshape((-1, 6))
    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=False)
    return (x_train, x_test, y_train, y_test)

def getLRM(x, y):
    model = LinearRegression().fit(x, y) 
    return model

def getGBRM(x, y):
    model = GradientBoostingRegressor(random_state=0).fit(x, y)
    return model

def getRFRM(x, y):
    model = RandomForestRegressor(random_state=0).fit(x, y)
    return model


