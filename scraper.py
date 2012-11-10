import urllib2
import urllib
import json
import pymongo
from datetime import datetime
import time
import calendar

###############################
SUBREDDIT = 'travel'
SLEEPMINUTES = 3
BOOTSTRAP_SIZE = 5

#assumes existence of a mongodb connection on the standard port
from pymongo import Connection
connection = Connection()
db = connection.reddit
collection = db.travel
###############################

def getPage(url) :
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 
	                      '/u/pltardif awesome scraper for the_reddit_project')]
	r = opener.open(url)
	json_data = json.loads(r.read().strip())
	return json_data['data']	

#UTC time in unix form
def now():
	return calendar.timegm(datetime.utcnow().utctimetuple())
	
def insertBootstrapPage(json_data,position_reference) :
	posts = []
	base_time = now()
	for item in json_data:
		item['data']['var'] = [{'time': base_time,
		                              'data':{
		                                'up' :   item['data']['ups'],
		                                'down' : item['data']['downs'],
		                                'com' :  item['data']['num_comments'],
		                                'pos' : (json_data.index(item) 
		                                        + 1 + position_reference)
		                              }}]
		item['data']['_id'] = item['data']['id'] #mongo uses '_id'
		del item['data']['id'] 
		posts.append(item['data'])
	collection.insert(posts) #bulk insert

def initialBootstrap(numPages) :
	for i in range(0,numPages):
		if i == 0:
			url = 'http://www.reddit.com/r/' + SUBREDDIT + '/.json?limit=100'
		else:
			url = ('http://www.reddit.com/r/' + SUBREDDIT + '/.json?limit=100&' 
			       + urllib.urlencode({'count':str(i*100),'after': page['after']}))
		page = getPage(url)
		insertBootstrapPage(page['children'],position_reference=i*100)

def getNewPosts():
	morePosts = True
	newPosts = []
	i = 0  #number of 100 post pages visited
	after = None
	while (morePosts) :	
		if not after:
			url = 'http://www.reddit.com/r/' + SUBREDDIT + '/new/.json?limit=100'
		else:
			url = ('http://www.reddit.com/r/' + SUBREDDIT + '/new/.json?limit=100&' 
			       + urllib.urlencode({'count':str(i*100),'after': after}))
		page = getPage(url)	
		if len(page['children']) > 0:
			for post in page['children']:
				if collection.find({'_id':post['data']['id']}).count() > 0:
					morePosts = False
					break
				else:
					post['data']['_id'] = post['data']['id'] #mongo uses '_id'
					del post['data']['id'] 
					newPosts.append(post['data'])
		if page['after'] :
			after = page['after']
			i+=1
		else:
			morePosts = False
	if len(newPosts) > 0:
		print str(newPosts)
		collection.insert(newPosts) #bulk insert
		print 'Added %i' % len(newPosts)
	else :
		print 'Nothing added'

def getAllIds():
	ids = set()
	for id in collection.find():
		ids.add(id['_id'])
	return ids

def assignVariableData():
	getNewPosts()
	ids = getAllIds()
	base_time = now()
	finished = False
	i = 0  #number of 100 post pages visited
	after = None
	while not (finished) :	
		if not after:
			url = 'http://www.reddit.com/r/' + SUBREDDIT + '/.json?limit=100'
		else:
			url = ('http://www.reddit.com/r/' + SUBREDDIT + '/.json?limit=100&' 
			       + urllib.urlencode({'count':str(i*100),'after': after}))
		page = getPage(url)
		for post in page['children']:
			if collection.find({'_id':post['data']['id']}).count() > 0:
				ids.remove(post['data']['id'])
				collection.update({'_id':post['data']['id']},
					              { '$push' :{'var': 
					                        {'time':base_time,
					                         'data':{
					                           'up' :   post['data']['ups'],
					                           'down' : post['data']['downs'],
					                           'com' :  post['data']['num_comments'],
					                           'pos' : (page['children'].index(post) 
					                                      + 1 + i*100)}}}})
		if len(ids) == 0:
			finished = True
		else:
			if page['after'] :
				after = page['after']
				i+=1
			else:
				finished = True
				#insert '?' for all remaining ids
				for id in ids:
					collection.update({'_id':id},{'$push':{'var':{'time':base_time,'data':'?'}}})
				
	print "Updated " + str(time.strftime("%d-%H:%M:%S", time.localtime()))
	
def main() :
	initialBootstrap(BOOTSTRAP_SIZE) # x* 100 post length pages
	print('Bootstrapped')
	while(True):
		time.sleep(SLEEPMINUTES*60)
		assignVariableData()

if __name__ == "__main__":
    main()
    
    