import pymongo
from itertools import *
import matplotlib.pyplot as plt
import matplotlib
from numpy import *
import pylab as lab

#####################
from pymongo import Connection
connection = Connection()
db = connection.reddit

COLLECTION_NAME = 'fitness'
collection = db.fitness
START_TIME = 1352955347
#TRAVEL = 1352938569
#FITNESS = 1352955347
#####################

parms = {'created_utc':{'$gte' : START_TIME}}
parms2 = {'created_utc':START_TIME}


def advancedTrajectoryReport():
	intervals = [
		[1,5,'blue'],
		[6,10,'blue'],
		[11,15,'blue'],
		[16,1000,'blue']
	]
	
	c = 1
	for i in intervals:	
		plt.subplot(220 + c)
		c += 1
		n = advancedTrajectories(i[0],i[1],i[2])
		plt.title('Max Rank %s-%s (n = %s)' % (i[0],i[1],n))
	plt.suptitle('Normalized rises for %s' % COLLECTION_NAME)
	plt.show()
	
def advancedTrajectories(maxRank,minRank,color):
	counter = 0
	for doc in collection.find(parms):
		tr = trajectory(doc['_id'],False,False)
		if len(tr) >= 10 and max(tr) != min(tr): 
			min_val = min(tr)
			if min_val >= maxRank and min_val <= minRank:
				trajectoryPlotNormalized(tr,color)
				counter += 1
	return counter

def basicTrajectoryReports():
	intervals = [
		(1,5),
		(6,10),
		(11,15),
		(16,25),
		(26,1000)
	]	
	for i in intervals:	trajectoryReportBasic(i[0],i[1])
		
def trajectoryReportBasic(maxRank,minRank):
	rises = []
	falls = []
	plats = []
	for doc in collection.find(parms):
		tr = trajectory(doc['_id'],False,False)
		if len(tr) >= 3: 
			data = trajectoryNormalizeTime(tr)
			min_val = min(tr)
			if min_val >= maxRank and min_val <= minRank:
				rises.append(data['rise']+1)
				falls.append(data['fall']+1)
				plats.append(data['plat'])
				
	rises = log(rises)
	falls = log(falls)
	plt.figure(figsize=(12,8))
	plt.subplot2grid((3,2),(0,0))
	plt.hist(rises)
	plt.title('log(rise)')
	plt.subplot2grid((3,2),(1,0))
	plt.hist(falls)
	plt.title('log(fall)')
	plt.subplot2grid((3,2),(0,1),rowspan=2)
	plt.hist2d(rises,falls)
	plt.xlabel('log(rise)')
	plt.ylabel('log(fall)')
	plt.subplot2grid((3,2),(2,0),colspan=2)
	plt.hist(plats,log=True)
	plt.title('Plateau length')
	plt.suptitle('Peaks from %s-%s (n=%s) in %s' % (maxRank, minRank, len(rises), COLLECTION_NAME))
	lab.savefig("%s-%s (%s).png" % (maxRank, minRank, COLLECTION_NAME))

def trajectoryPlotNormalized(tr,c='black'):
	plt.plot(trajectoryNormalizeTime(tr)['t'],trajectoryNormalizeRank(tr),color=c,alpha=0.2)
	plt.gca().set_xlim([-1,0])
	
def trajectoryNormalizeRank(tr):
	min_value = min(tr)
	max_value = max(tr)
	new_tr = []
	if max_value == min_value:
		for i in tr: new_tr.append(0.5)
	else:
		for i in tr: new_tr.append((max_value - i)/float(max_value - min_value))
	return new_tr

def trajectoryNormalizeTime(tr):
	#indices
	min_value = min(tr)
	min_index = 1000
	max_index = None
	for i in range(0,len(tr)): 
		if tr[i] == min_value: 
			max_index = max(i,max_index)
			min_index = min(i,min_index)
	times = []
	for i in range(0,len(tr)): 
		if i < max_index:
			value = -1 + i*(1/float(max_index))
		elif i == max_index:
			value = 0
		else:
			value = ((i-max_index)*1)/float(len(tr)-max_index-1)
		times.append(value)
	#plt.plot(times,tr)
	#plt.show()
	return {'t':times,'rise': min_index, 'fall': len(tr) - max_index, 'plat': max_index - min_index}
	
def getCollection():
	return collection

def subredditDistro():
	data = []
	for sub in collection.find():
		data.append(log(sub['data']['subscribers']+1)) #avoid zero errors
	plt.hist(data,log=True,histtype='step')
	plt.title('Subreddit log(size) vs. log(frequency)')
	plt.xlabel('Log(size)')
	plt.ylabel('Frequency')
	plt.show()

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
	
def trajectory(id,show=True,plot=True):
	query = {'_id':id}
	pos = []
	for item in collection.find_one(query)['var']:
		if item['data'] != '?' : 
			if item['data']['pos'] < 900:
				pos.append(item['data']['pos'])
	
	if plot:
		plt.plot(pos)
		plt.ylim((1,100))
		plt.xlim((0,50))
		if show: plt.show()
	return pos

if __name__ == '__main__':
    basicTrajectoryReports()		
		
