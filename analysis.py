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
	
	if show : 
		plt.plot(map(lambda x: len(ranks[x]),ranks))
		plt.show()
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
	
	if show: 
		plt.imshow(img)
		plt.show()
	return m

def topTrajectories(type='line'):
    #######################
	r = [1,2,3,4,5,6]
	rows = 3
	columns = 2
	#######################
	
	c = 1
	ranks = maxRankAchieved(False)
	for i in r:
		plt.subplot(rows*100 + columns*10 + c)
		c += 1
		if type == 'line':
			for tr in ranks[i]:
				trajectory(tr,False)
		elif type == 'box':
			topTrajectoriesPerGroup(ranks[i],False)

		plt.title('Max Rank = %s' % i)
		plt.ylim((1,20))
		plt.xlim((0,50))
	plt.show()

def topTrajectoriesPerGroup(ids,show=True):
	data = []
	for i in range(0,50): data.append([])
	
	for id in ids:
		query = {'_id':id}
		counter = 0
		for item in collection.find_one(query)['var']:	
			if counter == 50:
				break
			if item['data'] != '?':
				data[counter].append(item['data']['pos'])
			counter += 1
	plt.boxplot(data)
	if show:	plt.show()
	return data
	
def trajectory(id,show=True):
	query = {'_id':id}
	pos = []
	for item in collection.find_one(query)['var']:
		if item['data'] != '?' : pos.append(item['data']['pos'])
	
	plt.plot(pos)
	plt.ylim((1,100))
	plt.xlim((0,50))
	if show: plt.show()
	return pos
				
		
