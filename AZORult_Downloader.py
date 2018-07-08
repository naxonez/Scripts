#!/usr/bin/env python2

import requests, string, sys
from time import gmtime, strftime
import urllib2,cStringIO, zipfile
from bs4 import BeautifulSoup

def searchString(line):
	targets = {"SOFT","HOST","USER","PASS","UNKN","Email","session_key"}
	userLeak = list()
	for i in targets:
		if i in line:
			userLeak.append(line)
	return ''.join(userLeak)

def read_Remote(url):
	try:
    		remotezip = urllib2.urlopen(url)
    		zipinmemory = cStringIO.StringIO(remotezip.read())
    		zip = zipfile.ZipFile(zipinmemory)
    		for fn in zip.namelist():
            		ranks_data = zip.read(fn)
            		for line in ranks_data.split("\n"):
				searchString(line)

	except urllib2.HTTPError:
		pass

def get_all(url):
	try:
		complete_Url = url
		html_doc = urllib2.urlopen(complete_Url)
		soup = BeautifulSoup(html_doc,"lxml")
		for link in soup.find_all('a'):
			if "zip" in link.get('href'):
				return read_Remote(url+link.get('href'))
	except urllib2.HTTPError:
		pass

def main(argv):
	get_all("http://"+argv[0]+"files/")

if __name__ == '__main__':
  main(sys.argv[1:])
