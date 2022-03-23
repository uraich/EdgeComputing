from lis3dh import LIS3DH
from machine import Pin,SoftI2C
from lis3dh_const import *
import ustruct as struct
import sys

class LIS3DH_I2C(LIS3DH) :
    def __init__(self,scl=18,sda=23,sa0=19,cs=26,debug=False) :
        super().__init__(debug=debug)
        self.sa0=sa0
        self.cs=cs
        a0 = Pin(self.sa0,Pin.OUT) # This is the address bit of I2C
        a0.off()
        i2c_mode = Pin(self.cs,Pin.OUT)
        i2c_mode.on()              # chip select must be high for I2C mode
        self.i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        if not LIS3DH_I2C_ADDR in self.i2c.scan() :
            print("lis3dh is not connected to the I2C bus. Giving up...")
            sys.exit(-1)
        self.lis3dh_i2c_addr= LIS3DH_I2C_ADDR
        who_am_i = self.getID()
        if self.debug :
            print("who am i: 0x{:02x}".format(who_am_i))
        
    def read_byte(self,register) :
        return bytearray(self.i2c.readfrom_mem(self.lis3dh_i2c_addr,register,1))[0]
    
    def read_bytes(self,register,no_of_bytes) :
        tmp = bytearray(self.i2c.readfrom_mem(self.lis3dh_i2c_addr,register | 0x80 ,no_of_bytes))
        if self.debug :
            print("Read {:d} bytes from 0x{:02x}".format(no_of_bytes,register))
            print("Returned {:d} bytes: ".format(len(tmp)),end="")
            for i in range(len(tmp)) :
                print("0x{:02x} ".format(tmp[i]),end="")
            print("")
            
        return tmp

    def write_byte(self,register,value) :
        if self.debug :
            print("Debug: Writing 0x{:02x} to register 0x{:02x}".format(value,register))
        tmp = bytearray(1)
        tmp[0]=value
        self.i2c.writeto_mem(self.lis3dh_i2c_addr,register,tmp)

    def read_word(self,register):
        return struct.unpack('<h', self.read_bytes(register | 0x80, 2))[0]
