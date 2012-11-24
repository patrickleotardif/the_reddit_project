import pymongo
from itertools import *
import matplotlib.pyplot as plt
from numpy import *

#####################
from pymongo import Connection
connection = Connection()
db = connection.reddit

COLLECTION_NAME = 'travel'
collection = db.travel
START_TIME = 1352938569
#TRAVEL = 1352938569
#FITNESS = 1352955347
#####################

parms = {'created_utc':{'$gte' : START_TIME}}
parms2 = {'created_utc':START_TIME}

def upDownMatrix():
	ups = []
	downs =  [] 
	poss = []
	for doc in collection.find(parms):
		subparms  = {'_id':doc['_id']}
		up = 0
		down = 0
		pos = 5000
		for item in collection.find_one(subparms)['var']:
			if item['data'] != '?' : 
				up = max(up,item['data']['up'])
				down = max(down,item['data']['down']+1) #to make log stuff work
				pos = min(pos,item['data']['pos'])
		if up+down != 0:
			ups.append(up)
			downs.append(down)
			poss.append(min(pos,10))
			
	
	xmin = min(log(ups))
	xmax = max(log(ups))
	ymin = min(log(downs))
	ymax = max(log(downs))
	#poss = log(poss)
	
	#plt.hexbin(log(ups),log(downs), bins='log', cmap=plt.cm.YlOrRd_r)
	plt.scatter(log(ups),log(downs),c=poss,s=100)
	plt.axis([xmin, xmax, ymin, ymax])
	plt.gray()
	plt.colorbar()
	
	plt.show()

			
def distroReport():
	c = 1	
	for type in (('pos',None),('com',None),('up','loglog'),('down','loglog')):
		plt.subplot(220 + c)
		distro(type[0],type[1],False)
		c += 1
	plt.show()
		
#options for type = up/down/com/pos
def distro(type,plot=None,show=True):	
	data = {}
	
	if type in ('up','down','com'):
		INITIAL = 0
		FUNC = 'max'
	else: #pos
		INITIAL = 5000
		FUNC = 'min'
		
	for doc in collection.find(parms):
		subparms  = {'_id':doc['_id']}
		s = INITIAL
		for item in collection.find_one(subparms)['var']:
			if item['data'] != '?' : 
				if FUNC == 'max':
					s = max(s,item['data'][type])
				else : #min or pos
					s = min(s,item['data'][type])
		if s != INITIAL:
			if s in data:
				data[s].append(doc['_id'])
			else:
				data[s] = [doc['_id']]
	
	if not plot:
		plt.plot(map(lambda x: len(data[x]),data))
	elif plot == 'loglog':
		plt.loglog(map(lambda x: len(data[x]),data))
	
	if type in ('up','pos'):
		plt.xlim(xmin=1)
	
	plt.ylabel('number of posts')
	plt.xlabel('number of %s' % type)
	plt.title('Distribution of %s in %s' % (type, COLLECTION_NAME))
		
	if show : plt.show()
	
	return data

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
	ranks = distro('pos',show=False)
	for i in r:
		plt.subplot(rows*100 + columns*10 + c)
		c += 1
		if type == 'line':
			for tr in ranks[i]:
				trajectory(tr,False)
		elif type == 'box':
			topTrajectoriesPerGroup(ranks[i],False)

		plt.title('Max Rank = %s (n= %s)' % (i,len(ranks[i])))
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
				
		
