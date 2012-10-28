import urllib2
import urllib
import json
import pymongo

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

def insertFullPage(json_data) :
	posts = []
	for item in json_data:
		item['data']['_id'] = item['data']['id'] #mongo uses _id
		del item['data']['id'] 
		posts.append(item['data'])
	collection.insert(posts) #bulk insert

def initialBootstrap(numPages) :
	for i in range(0,numPages):
		if i == 0:
			url = 'http://www.reddit.com/.json'
		else:
			url = ('http://www.reddit.com/.json?' 
			       + urllib.urlencode({'count':str(i*25),'after': after}))
		json_data = getPage(url)
		insertFullPage(json_data['children'])
		after = json_data['after']
		
def main() :
	initialBootstrap(3)

if __name__ == "__main__":
    main()
    
    