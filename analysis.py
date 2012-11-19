import pymongo
import matplotlib.pyplot as plt


#####################
from pymongo import Connection
connection = Connection()
db = connection.reddit

collection = db.travel
#TRAVEL = 1352938569
#FITNESS = 1352955347
#####################

parms = {'created_utc':{'$gte' : START_TIME}}
parms2 = {'created_utc':START_TIME}

def maxRankAchieved(show=True):	
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
	if show : plt.show()
	return ranks

def completion_matrix(show=True):
	#Get the time points to be used
	m = collection.find_one(parms2,{'var.time'})['var']
	new_m = []
	for i in range(0,len(m)):
		if i % 10 == 0 :
			new_m.append(m[i])
	m = new_m
	
	counter = len(m)
	for pt in m:
		counter -= 1
		pos = []
		print counter
		for doc in collection.find(parms):
			for docpt in doc['var']:
				if docpt['time'] > (pt['time']-30) and docpt['time'] < (pt['time']+30):
					if docpt['data'] != '?' : 
						pos.append(docpt['data']['pos'])
						break;
		pt['pos'] = pos
	
	img = []
	for item in m:
		row = [0] * 100
		for p in item['pos']:
			if p <= 100 : row[p-1] = 1
		img.append(row)
	plt.imshow(img)
	if show: plt.show()
	return m

def trajectory(id,show=True):
	query = {'_id':id}
	pos = []
	for item in collection.find_one(query)['var']:
		if item['data'] != '?' : pos.append(item['data']['pos'])
	print pos
	plt.plot(pos)
	plt.ylim((1,100))
	plt.xlim((0,50))
	if show: plt.show()
	return pos
				
		
