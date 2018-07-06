#!/usr/bin/env python2

#script para obtener el C&C de una muestra unpacked de lokibot (desktop)

import sys

def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
	return ((num == 0) and  "0" ) or ( baseN(num // b, b).lstrip("0") + numerals[num % b])

def main():

	if len(sys.argv) < 2:
    		sys.exit('[*] ERROR - Introducir nombre fichero...')

	with open(sys.argv[1], "rb") as f:
		f.seek(0x00018070)
		url = f.read(100)
		s=""
		for hexa in url:
			if hex(ord(hexa)) != "0x0" and hex(ord(hexa)) != "0x90":
				s +=hex(ord(hexa))[2:]

		if hex(ord(s[0])) == "0x39":
			print "[*] Hash found: "+ s
		else:
			sys.exit("ERROR - Hash not found")

	key=baseN(int(255),2)
	sol=""
	for i in xrange(0,len(s)-1,2):
    		sol=sol+chr(int(str(baseN(int(s[i]+s[i+1],16),2)),2)^int(key,2))
	print "[*] Final URL: " + sol


if __name__ == "__main__":
    main()
