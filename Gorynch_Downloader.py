import requests, string, sys
from time import gmtime, strftime
import urllib2,cStringIO, zipfile
from bs4 import BeautifulSoup

def searchString(line):
	targets = {"User"}
	userLeak = list()
	for i in targets:
		if i in line:
			userLeak.append(line)
	print userLeak
	return ''.join(userLeak)

def read_Remote(url):
	print url
	data = urllib2.urlopen(url) # it's a file like object and works just like a file
	for line in data: # files are iterable
    		searchString(line)


def get_all(url):
	try:
		paths = {"dump","ftp","kyl","mail","pass","rdp","scr","wallet"}
		for i in paths:
			html_doc = urllib2.urlopen(url+i)
			soup = BeautifulSoup(html_doc,"lxml")
			for link in soup.find_all('a'):
					if not "logs" in link.get('href'):
						read_Remote(url+i+"/"+link.get('href'))

	except urllib2.HTTPError:
		pass


def main(argv):
  get_all("http://"+argv[0]+"logs/")

if __name__ == '__main__':
  main(sys.argv[1:])
