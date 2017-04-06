import json
import subprocess
import sqlite3
import requests
import datetime

sqlite_file = "XXXX.db" # create table payloadBankers(md5,family,date, PRIMARY KEY(md5));
bot_id = "XXXXX"
chat_id = XXXX

def saveToDB(md5,family):
	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()
	try:
		c.execute("INSERT INTO payloadBankers(md5,family,date) VALUES('"+md5+"','"+family+"','"+str(datetime.date.today())+"')")
		response = requests.post(
   				 	url='https://api.telegram.org/bot{0}/{1}'.format(bot_id, "sendMessage"),
    					data={'chat_id': chat_id, 'text': "New Malware Detected!! "+ md5 + " " + family}
		).json()


	except:
		pass

	conn.commit()
	conn.close()

def main():
	malwareFamily = ["Zusy.Generic","ursnif","zbot","zloader","ramnit","banker","dridex"]
	s=subprocess.check_output(["python3","vxapi.py","get_feed","1"])
	jsonOutput = json.loads(s)

	for i in jsonOutput['data']:
		for j in malwareFamily:
			try:
				if(i['vxfamily'] in j):
					saveToDB(i['md5'],i['vxfamily'])
			except:
				pass

			try:
				if(i['description'] in j):
					saveToDB(i['md5'],i['description'])
			except:
				pass

			try:
				for x in i['tags']:
					if(x in j):
						saveToDB(i['md5'],x)
			except:
				pass

if __name__ == "__main__":
    main()
