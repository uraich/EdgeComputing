#!/usr/bin/python3

a = bytearray(b'\xFB\x00\x00\x3E\x00\x0B\x00\x36\x00\x01\x00\x02\x00\x03\x00\x00')
b = bytearray(b'\xFB\x00\x00\x3E\x00\x0B\x00\x36\x00\x01\x00\x02\x00\x03\x00\x00')
if a != b:
    print("different")
else:
    print("equal")