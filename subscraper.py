import urllib2
import urllib
import json
import pymongo

###############################
BOOTSTRAP_SIZE = 5

#assumes existence of a mongodb connection on the standard port
from pymongo import Connection
connection = Connection()
db = connection.reddit1
collection = db.subreddits
###############################

def getPage(url):
	print url
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', '/u/kmuthura awesome scraper for the_reddit_project')]
	r = opener.open(url)
	json_data = json.loads(r.read().strip())
	return json_data['data']	

#scrape subreddit info from a page (25 subreddits/page)
def insertBootstrapPage(json_data):
	for item in json_data:
		item['data']['var'] = [{ 'data':{
		                            'name' : item['data']['display_name'],
		                            'icon' : item['data']['header_img'],
		                            'url' : item['data']['url'],
									'subscribers' : item['data']['subscribers'],
									'namecode' : item['data']['name'],
									'nsfw' : item['data']['over18']
		                      }}]
		item['data']['_id'] = item['data']['id'] #mongo uses '_id'
		del item['data']['id'] 
	collection.insert(item['data']) #bulk insert

#traverse the pages
def initialBootstrap(numPages):
	for i in range(0,numPages):
		if i == 0:
			url = 'http://www.reddit.com/reddits/.json'
		else:
			url = ('http://www.reddit.com/reddits/.json?' + urllib.urlencode({'count':str(i*25),'after': page['after']}))
		page = getPage(url)
		print url
		insertBootstrapPage(page['children'])

def main() :
	initialBootstrap(BOOTSTRAP_SIZE) 
	print('Bootstrapped')

if __name__ == "__main__":
    main()
    