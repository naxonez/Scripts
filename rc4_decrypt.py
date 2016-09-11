#!/bin/python

def rc4_pass_bytes(param1, param2):
    temp_ba1 = bytearray()
    temp_ba2 = bytearray()

    temp_1 = 0
    while(temp_1 < 256):
        temp_ba1.append(temp_1)
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    while(temp_1 < 256):
        temp_2 = temp_2 + temp_ba1[temp_1] + param1[temp_1 % len(param1)] & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    temp_4 = 0

    while(temp_4 < len(param2)):
        temp_1 = temp_1 + 1 & 255
        temp_2 = temp_2 + temp_ba1[temp_1] & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_ba2.append(param2[temp_4] ^ temp_ba1[temp_ba1[temp_1] + temp_ba1[temp_2] & 255])
        temp_4 += 1

    return temp_ba2

def rc4_pass_text(param1,param2):
    temp_ba1 = bytearray()
    temp_ba2 = bytearray()

    temp_1 = 0
    while(temp_1 < 256):
        temp_ba1.append(temp_1)
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    while(temp_1 < 256):
        temp_2 = temp_2 + temp_ba1[temp_1] + ord(param2[temp_1 % len(param2)]) & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    temp_4 = 0

    while(temp_4 < len(param1)):
        temp_1 = temp_1 + 1 & 255
        temp_2 = temp_2 + temp_ba1[temp_1] & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_ba2.append(param1[temp_4] ^ temp_ba1[temp_ba1[temp_1] + temp_ba1[temp_2] & 255])
        temp_4 += 1


def main():
    #RC4 binary password
    param2 = bytearray(open("binaryData//1_t.tyeheyazbxhhv.bin","rb").read())
    param1 = bytearray(open("binaryData//2_t.wigyuqyavs.bin", "rb").read())
    data = rc4_pass_bytes(param1, param2)
    f = open("Decrypted.bin", "wb")
    f.write(data)
    f.close()

    #RC4 text password
    param2 = bytearray(open("binaryData//1_t.tyeheyazbxhhv.bin","rb").read())
    param1 = "XxXXxX"
    data = rc4_pass_bytes(param1, param2)
    f = open("Decrypted.bin", "wb")
    f.write(data)
    f.close()

if __name__ == '__main__':
    main()
