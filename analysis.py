import pymongo
import matplotlib.pyplot as plt


#####################
from pymongo import Connection
connection = Connection()
db = connection.reddit

collection = db.fitness

START_TIME = 1352955347
#TRAVEL = 1352938569
#FITNESS = 1352955347
#####################

parms = {'created_utc':{'$gte' : START_TIME}}

def maxRankAchieved():	
	ranks = {}
	for doc in collection.find(parms):
		subparms  = {'_id':doc['_id']}
		s = 5000 #or something else too big
		for item in collection.find_one(subparms)['var']:
			if item['data'] != '?' : s = min(s,item['data']['pos'])
		if s : 
			if s in ranks:
				ranks[s].append(doc['_id'])
			else:
				ranks[s] = [doc['_id']]
	plt.plot(map(lambda x: len(ranks[x]),ranks))
	plt.show()
	


