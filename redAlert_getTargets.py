import requests
import base64
import re
import sys

def main():

        if len(sys.argv) < 2:
                print "[ERROR] Usage: getTargets.py IP:PORT"
                print "Example: getTargets.py 91.218.114.16:7878"
        else:
		urlStbi = "http://"+sys.argv[1]
		payload = "eyJvcyI6IkFuZHJvaWQgNC40LjIiLCJtb2RlbCI6IlNhbXN1bmcgU0FNU1VORy1TTS1OOTAwQSIsImhhc2giOiJndGNyNWQ0bTJvYThyeTNwdDJqa3JndnhqM2NwNWtrMjMyNWFoenF2IiwiaW1laSI6IjUzODQzNDMyMzAyMzg2NSIsImljY2lkIjoiMzEyMDE2MDA0MTQzNjI0NDg3OTIiLCJjb250cm9sX251bWJlciI6ImRlbGV0ZSBsYXRlciIsIm51bWJlciI6IjQ0MDEwMzYyNDQ4NzkyMCIsInR5cGUiOiJzdGJpIiwibGFuZyI6ImVzIn0=" 

		r =requests.post(urlStbi+"/stbi",data=payload)
		packages_list ='''{"templates_names":["es.univia.unicajamovil"],"type":"sban","lang":"es","imei":"538434323023865","bot_id":"'''+r.text+'''"}''' ### Poner el nombre de los paquetes a consultar
		print "[*] BotID: " + r.text
		encoded_payload = base64.b64encode(packages_list)
		r =requests.post(urlStbi+"/sban",data=encoded_payload)
		print "[*] Targets Affected: "+ r.text

if __name__ == "__main__":
   main()
