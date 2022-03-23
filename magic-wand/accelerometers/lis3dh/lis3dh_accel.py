# lis3dh_accel.py: example program for use of the LIS3DH class
# Initalizes the lis3dh chip
# Sets the data rate to 1 Hz
# Sets the chip to high resolution
# Checks if new data are available
# Reads the x,y,z, acceleration data and prints the result
# Copyright (c) U. Raich, March 2022
# This program is part of the course on TinyML at the University of Cape Coast, Ghana
# It is released under the MIT license

from lis3dh_i2c import LIS3DH_I2C
from lis3dh_const import *
from utime import sleep_ms

# Create a LIS3DH onject running on the I2C bus
lis3dh_i2c = LIS3DH_I2C()
print("Enable debugging information")
lis3dh_i2c.debugging = False

print("Reboot the device")
lis3dh_i2c.boot = True
sleep_ms(5)
# ctrl5 = lis3dh_i2c.ctrl_reg5
print("CTRL_REG_5 after boot: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5))
print("STATUS register after boot: 0x{:02x}".format(lis3dh_i2c.status))

# set the data rate to 1 Hz
print("Set data rate to 1 Hz")
lis3dh_i2c.data_rate = RATE_1HZ

#  enable all axes, normal mode
lis3dh_i2c.all_axis_enable = True

# set the BDU bit in CTRL_REG 4, see section 3.7 of the data sheet
print("Set the Block Data Update (BDU) bit in CTRL_REG4. Needed to access the ADCs and the temperature sensor")
lis3dh_i2c.block_data_update = True

# enable high resolution
print("Set to high resolution")
lis3dh_i2c.high_res = True

print("CTRL_REG1: 0x{:02x}".format(lis3dh_i2c.ctrl_reg1))
print("CTRL_REG2: 0x{:02x}".format(lis3dh_i2c.ctrl_reg2))
print("CTRL_REG4: 0x{:02x}".format(lis3dh_i2c.ctrl_reg4))
print("CTRL_REG5: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5))
print("Data rate: ",lis3dh_i2c.print_rate(lis3dh_i2c.data_rate))

# clear data available
accel = lis3dh_i2c.accel_raw

while True:
    # wait until data is available
    if lis3dh_i2c.zyx_data_available :
        accel = lis3dh_i2c.accel
        print("accel_x: {:4.2f}, accel_y: {:4.2f}, accel_z: {:4.2f}".format(accel[0],accel[1],accel[2]))
    else :
        sleep_ms(1)

