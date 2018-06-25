import hashlib
import sys

def main():
	if len(sys.argv) < 3:
		print "[ERROR] Usage: getHashWithSalt.py DATE MD5"
		print "Example: getHashWithSalt.py 9/18/2017 jfkbl6fm02mfk0rcuva0i4vgoxyej2z8tvlr01jq"
	else:
		hash = hashlib.md5( sys.argv[1].encode() + sys.argv[2].encode()).hexdigest()
		print "[*] Parameters"
		print "Salt:" + sys.argv[1]
		print "Hash:" + sys.argv[2]
		print "[*] Result"
		print "Final Hash: " + hash # Store these
		print "Final Twitter Handler: https://twitter.com/intent/user?user_id=" + hash[0:16]
if __name__ == "__main__":
   main()
