def xor(data, key):
    l = len(key)
    return bytearray((
        (data[i] ^ key[i % l]) for i in range(0,len(data))
    ))

data = bytearray(open('1_BINARY', 'rb').read())
key = bytearray("PASSWORD")
a = xor(data, key)
print a
