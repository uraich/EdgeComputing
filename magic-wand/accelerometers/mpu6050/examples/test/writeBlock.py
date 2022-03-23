from MPU6050 import MPU6050
from MPU6050_const import *

from utime import sleep_ms

m6050 = MPU6050(debug=True)

m6050.setMemoryBank(0)
m6050.setMemoryStartAddress(0)

# get MPU hardware revision
m6050.setMemoryBank(0x10, True, True)
m6050.setMemoryStartAddress(0x06)
print("Checking hardware revision...")
print("Revision @ user[16][6] = 0x{:02x}".format(m6050.readMemoryByte()))

print("Resetting memory bank selection to 0...")
m6050.setMemoryBank(0)
m6050.setMemoryStartAddress(0)

data = 0x55
m6050.writeMemoryByte(data)

m6050.setMemoryStartAddress(0)
retData = m6050.readMemoryByte()

print("data written: 0x{:02x}, data read back: 0x{:02x}".format(data,retData))

data = bytearray(b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\
\x99\xaa\xbb\xcc\xdd\xee\xff')

print("Data written:")
for i in range(len(data)):
    print("0x{:02x} ".format(data[i]),end = "")
print("")

m6050.writeMemoryBlock(data,0,0,True)
verify_data = m6050.readMemoryBlock(16,0,0)
print("Data read back:")
for i in range(len(verify_data)):
    print("0x{:02x} ".format(verify_data[i]),end = "")
print("")
