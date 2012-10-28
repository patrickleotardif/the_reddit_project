import urllib2
import urllib
import json
import pymongo
from datetime import datetime
import calendar


#assumes existence of a mongodb connection on the standard port
from pymongo import Connection
connection = Connection()
db = connection.test_database
collection = db.test_collection

def getPage(url) :
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 
	                      'pltardif scraper for the_reddit_project')]
	r = opener.open(url)
	json_data = json.loads(r.read().strip())
	return json_data['data']	

#UTC time in unix form
def now():
	return calendar.timegm(datetime.utcnow().utctimetuple())
	
def insertBootstrapPage(json_data,position_reference) :
	posts = []
	for item in json_data:
		item['data']['var'] = [{'time':now(),
		                              'data':{
		                                'up' :   item['data']['ups'],
		                                'down' : item['data']['downs'],
		                                'com' :  item['data']['num_comments'],
		                                'pos' : (json_data.index(item) 
		                                        + 1 
		                                        + position_reference)
		                              }}]
		item['data']['_id'] = item['data']['id'] #mongo uses '_id'
		del item['data']['id'] 
		posts.append(item['data'])
	collection.insert(posts) #bulk insert

def initialBootstrap(numPages) :
	for i in range(0,numPages):
		if i == 0:
			url = 'http://www.reddit.com/r/travel/.json?limit=100'
		else:
			url = ('http://www.reddit.com/r/travel/.json?limit=100&' 
			       + urllib.urlencode({'count':str(i*100),'after': page['after']}))
		page = getPage(url)
		insertBootstrapPage(page['children'],position_reference=i*100)


def assignVariableData():
	#do stuff
	print 'lala'
		
def main() :
	initialBootstrap(3) # x* 100 post length pages


if __name__ == "__main__":
    main()
    
    