#!/usr/bin/python3

def sub1(data, dataSize, bank=7, address=0xaaaa, verify=True):
#    sub2(data, dataSize, bank=bank, address=address, verify=True,useProgMem=True)
    sub2(data, dataSize, bank, address, verify,useProgMem=True)

def sub2(data, dataSize, bank, address, verify, useProgMem=True):
    print("data: {}, dataSize: {:d}, bank: {:d}, address: 0x{:04x}, verify: {:d}, useProgMem: {:d}".format(
        data, dataSize, bank, address, verify, useProgMem))

data = bytearray(b'\x3a\x34\xaa\x55')
sub1(data,3)
