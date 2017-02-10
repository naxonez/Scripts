#!/bin/python

def decrypt_rc4(param1,param2):
    if isinstance(param1,bytearray):
        if isinstance(param2,bytearray):
            if len(param1) > len(param2):
                key  = param2
                data = param1
            else:
                key  = param1
                data = param2
        else:
             if isinstance(param2,str):
                  key = param2
                  data = param1
             else:
                  print "[*] Error, param2 is not a valid input"
                  sys.exit()
    else:
        if isinstance(param1,str):
              if isinstance(param2,bytearray):
                  key  = param1
                  data = param2
              else:
                  if len(param1) > len(param2):
                      key  = param2
                      data = param1
                  else:
                      key  = param1
                      data = param2
        else:
            print "[*] Error, param1 is not a valid input"
            sys.exit()

    temp_ba1 = bytearray()
    temp_ba2 = bytearray()

    temp_1 = 0
    while(temp_1 < 256):
        temp_ba1.append(temp_1)
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    while(temp_1 < 256):
        if isinstance(key,str):
             temp_2 = temp_2 + temp_ba1[temp_1] + ord(key[temp_1 % len(key)]) & 255
        else:
             temp_2 = temp_2 + temp_ba1[temp_1] + key[temp_1 % len(key)] & 255

        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    temp_4 = 0

    while(temp_4 < len(data)):
        temp_1 = temp_1 + 1 & 255
        temp_2 = temp_2 + temp_ba1[temp_1] & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_ba2.append(data[temp_4] ^ temp_ba1[temp_ba1[temp_1] + temp_ba1[temp_2] & 255])
        temp_4 += 1

    return temp_ba2

def main():
    #RC4 text password
    param2 = bytearray(open("BINARY_FILE.bin","rb").read())
    param1 = "PASSWORD"
    data = decrypt_rc4(param1, param2)
    f = open("Decrypted.bin", "wb")
    f.write(data)
    f.close()

if __name__ == '__main__':
	main()
