
import numpy as np
import datetime
import pandas as pd
from pymongo import MongoClient

client = MongoClient(port=27017)
db=client.nhl
team_coll = db.seasonaverages
averages = db.leagueaverages

seasonId = 20212022
filter = {"seasonId": seasonId}
cursor = team_coll.find(filter)
df = pd.DataFrame(list(cursor))
del df['_id']
del df['teamId']
del df['seasonId']
df2 = df.mean()
average = df2.to_dict()
values = {"$set": average}
averages.update_one(filter, values)
print("done")