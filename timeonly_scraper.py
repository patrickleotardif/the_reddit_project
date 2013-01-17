import urllib2
import urllib
import json
import pymongo
from datetime import datetime
import time
import calendar

###############################
SLEEPMINUTES = 1
BOOTSTRAP_SIZE = 5

#assumes existence of a mongodb connection on the standard port
from pymongo import Connection
connection = Connection()
db = connection.reddit
collection = db.timeonly
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
		posts.append( {'_id' : item['data']['id'],'time': item['data']['created_utc']  } )
	collection.insert(posts) #bulk insert

def initialBootstrap(numPages) :
	for i in range(0,numPages):
		if i == 0:
			url = 'http://www.reddit.com/.json?limit=100'
		else:
			url = ('http://www.reddit.com/.json?limit=100&' 
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
			url = 'http://www.reddit.com/new/.json?limit=100'
		else:
			url = ('http://www.reddit.com/new/.json?limit=100&' 
			       + urllib.urlencode({'count':str(i*100),'after': after}))
		page = getPage(url)	
		if len(page['children']) > 0:
			for post in page['children']:
				if collection.find({'_id':post['data']['id']}).count() > 0:
					morePosts = False
					break
				else:
					newPosts.append({'_id':post['data']['id'], 'time':post['data']['created_utc']})
		if page['after'] :
			after = page['after']
			i+=1
		else:
			morePosts = False
	if len(newPosts) > 0:
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
	page = getPage('http://www.reddit.com/.json?limit=25')
	for post in page['children']:
		if collection.find({'_id':post['data']['id']}).count() > 0:
			collection.update({'_id':post['data']['id']},
				              { '$push' :{'front': now()}})
						
	print "Updated " + str(time.strftime("%d-%H:%M:%S", time.localtime()))
	
def main() :
	#initialBootstrap(BOOTSTRAP_SIZE) # x* 100 post length pages
	#print('Bootstrapped')
	while(True):
		assignVariableData()
		time.sleep(SLEEPMINUTES*60)

if __name__ == "__main__":
    main()
    
    