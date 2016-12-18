from twitter import *
from flask import Flask, render_template, request
from threading import Thread
import time, json


application = Flask(__name__)
application.secret_key = "my handle is root"
twitter = Twitter(auth = OAuth("3284409438-1fi2IudIB4ViaXpvREuYwAAe8VK0iB8PER1qUiE", "FeMEtOoL25hZNVNrRagNSxxwKhPILmrtxVexUdI4dEtaw", "YjkfScgxRbL29b0lY5mbgQtyG", "te4u9k3GNZlv5nELUpSa70wlfPLvTxVQ5flQFKaOImirEGA900"))


global user_data

user_data = {}

#-----------------------------------------------------------------------
# This is a thread function which does all the processing. It takes coords
# of the user and hits the Twitter's API in fixed intervals. The new data
# received is updated in the global dictionary.
#-----------------------------------------------------------------------
def fetch_tweets_thread(latitude, longitude):

	global user_data

	max_range    = 800 	# Radius in Km		
	last_id      = None # Last User ID
	user_key     = str(int(latitude)) + str(int(longitude)) # Key used in dictionary

	if user_data.has_key(user_key)==False:
		user_data[user_key] = []

	while True:

		query = twitter.search.tweets(q = "", geocode = "%f,%f,%dkm" % (latitude, longitude, max_range), max_id = last_id)

		for result in query["statuses"]:
			#----------------------------------------------------------------------
			# only process a result if it has a geolocation
			#----------------------------------------------------------------------
			if result["geo"]:
				user      = result["user"]["screen_name"]
				text      = result["text"]
				text      = text.encode('ascii', 'replace')
				latitude  = result["geo"]["coordinates"][0]
				longitude = result["geo"]["coordinates"][1]
				row       = [ user, text, latitude, longitude ]

				user_data[user_key].append(row)

			last_id = result["id"]

		time.sleep(10)

#-----------------------------------------------------------------------
# This route is accessed when the application starts. 
#-----------------------------------------------------------------------
@application.route('/')
def index():
	return render_template('index.html')

#-----------------------------------------------------------------------
# This route is used for polling purpose. Every client pings this route
# in a fixed intervals to check if there is any new tweet. 
#-----------------------------------------------------------------------
@application.route('/markers', methods=['POST'])
def getUpdatedPositions():
	latitude  = request.json['lat'] 
	longitude = request.json['lng']
	user_key  = str(int(latitude)) + str(int(longitude))

	if user_data.has_key(user_key)==False:
		user_data[user_key] = []

	res_obj = []

	for key, items in user_data.iteritems():
		for item in items:
			res_obj.append(item)

	json_obj = json.dumps({'data':res_obj})

	return json_obj

#-----------------------------------------------------------------------
# Post Request is sent on this route whenever a user joins. 
#-----------------------------------------------------------------------
@application.route('/post_position', methods=['POST'])
def find_tweets():
	# Fetch coordinates from the JSON Request
	latitude  = request.json['lat'] 
	longitude = request.json['lng']
	# Fire a new thread
	thread_obj = Thread(target = fetch_tweets_thread, args = (latitude, longitude, ))
	thread_obj.start()

	return 'Success'


if __name__=='__main__':
	application.run(debug=True)
