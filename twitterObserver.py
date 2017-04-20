#!/usr/bin/env python
# coding=utf8

from twython import Twython
import datetime
import sqlite3
import requests

sqlite_file = "database.db" #create table bankerTweets(TweetId,UserName,Text,Date, PRIMARY KEY(TweetId));
bot_id = "XXXXX"
chat_id = "XXXX"

def searchMalware(t,malware):
	search = t.search(q=malware + " -filter:retweets  since:"+str(datetime.date.today()), count=1000)
	tweets = search['statuses']
	return tweets

def saveToDB(userName,tweet):
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        try:

                print "%s :: %s :: %s :: %s" % (str(datetime.date.today()), tweet['id_str'] , userName[0]['screen_name'] , tweet['text'])
                c.execute("INSERT INTO bankerTweets(TweetId, UserName, Text ,Date) VALUES(?,?,?,?)", (tweet['id_str'], userName[0]['screen_name'], tweet['text'], str(datetime.date.today()) ) )
                response = requests.post(
                        url='https://api.telegram.org/bot{0}/{1}'.format(bot_id, "sendMessage"),
                        data={'chat_id': chat_id, 'text': userName[0]['screen_name']+": "+tweet['text']}
                ).json()
                print 'Found!, sending over to telegram..'
        except sqlite3.IntegrityError as e:
                print "INTEGRITY ERROR: %s" % e
        except sqlite3.OperationalError as e:
                print "OPERATIONAL ERROR: %s" % e

        conn.commit()
        conn.close()

def main():
	malwareToSearch = ['#Dridex','#Trickbot','#Tinba','#Zloader','#Urlzone', '#ursnif','#shiotob']
	botnetToSearch = ['#Necurs','#Cutwail']
	TWITTER_APP_KEY = 'XXXX' #supply the appropriate value
	TWITTER_APP_KEY_SECRET = 'XXXX' 
	TWITTER_ACCESS_TOKEN = 'XXXXX'
	TWITTER_ACCESS_TOKEN_SECRET = 'XXXX'

	t = Twython(app_key=TWITTER_APP_KEY,
        	    app_secret=TWITTER_APP_KEY_SECRET,
            	    oauth_token=TWITTER_ACCESS_TOKEN,
            	    oauth_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

	#Malware
	for malware in malwareToSearch:
		tweets = searchMalware(t,malware)
		for tweet in tweets:
			userName = t.lookup_user(user_id=tweet['user']['id'])
			saveToDB(userName,tweet)
	#Botnet
	for malware in botnetToSearch:
		tweets = searchMalware(t,malware)
		for tweet in tweets:
			userName = t.lookup_user(user_id=tweet['user']['id'])
			saveToDB(userName,tweet)

if __name__ == "__main__":
    main()

#Creditos: 
#http://stackoverflow.com/questions/14156625/fetching-tweets-with-hashtag-from-twitter-using-python
#http://stackoverflow.com/questions/31197659/how-we-should-send-query-to-telegram-bot-api
