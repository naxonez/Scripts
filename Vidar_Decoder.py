# -*- coding: utf-8 -*-
import sys
import pefile
import struct
import string

def xorDecrypt(str,key):

    kp = 0
    newbuf = []

    for i in range(len(str)):
        newchar = ord(str[i]) ^ ord(key[kp])
        newbuf.append(chr(newchar))

        kp = kp + 1
        if kp >= len(key):
            kp = 0

    return ''.join(newbuf).encode('hex')


def main():
	pe = pefile.PE(sys.argv[1])
	rdata = pe.sections[1].get_data()
	start = rdata.find("string too long")
	data = rdata[start+len("string too long"):]
	xorKey = ""
	for i in data.split("\x00"):
		if(i != ""):
			if xorKey == "":
				xorKey = i.encode("hex")
			else:
				#End decrypt
				if(i == "APPDATA"):
					exit(0)

				output = xorDecrypt(i,xorKey.decode("hex")).decode("hex")
				if(all(c in string.printable for c in output) and all(c in string.printable for c in i)):
					if(len(i) > 2 and len(output) > 2):
						if(len(output.decode('utf-8')) and len(i) > 3):
							print("=====================")
							print("Encrypted : "+i)
							print("Key : " + xorKey)
							print("Decrypted : "+output.decode('utf-8'))
							print("=====================")

				xorKey = ""

if __name__ == "__main__":
	main()
