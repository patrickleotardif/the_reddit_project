import json

FILENAME = 'fitness.json'
START_POS = 500 #since these are the ones we tracked right from the beginning

file = open(FILENAME,'r')
out = open('trajectories.csv','w')
items = []

for line in file:
	items.append(json.loads(line))

for item in items[START_POS:]:
	for line in item['var']:
		if line['data'] != '?':
			out.write('%s,%s,%s\n' % (item['_id'],line['time']-item['created_utc'], line['data']['pos']))

out.close()
	
	