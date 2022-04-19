# lis3dh_fifo.py: Reads the accelerometer data from the fifo
# Copyright (c) U. Raich, March 2022
# This program is part of the course on TinyML at the University of Cape Coast, Ghana
# It is released under the MIT license

from lis3dh_i2c import LIS3DH_I2C
from lis3dh_const import *
from utime import sleep_ms

# Create a LIS3DH onject running on the I2C bus
lis3dh = LIS3DH_I2C()
print("Enable debugging information")
lis3dh.debugging = False

print("Reboot the device")
lis3dh.boot = True
sleep_ms(5)
# ctrl5 = lis3dh.ctrl_reg5
print("CTRL_REG_5 after boot: 0x{:02x}".format(lis3dh.ctrl_reg5))

# set the data rate to 100 Hz
print("Set data rate to 100 Hz")
lis3dh.data_rate = RATE_100HZ

# enable high resolution
print("Set to high resolution")
lis3dh.high_res = True

# set FIFO to FIFO mode
print("Seting FIFO to FIFO mode")
lis3dh.fifo_mode = FIFO_MODE_FIFO
print("FIFO mode is now " + lis3dh.print_fifo_mode(lis3dh.fifo_mode))
#enable the FIFO
lis3dh.fifo_enable = True

print("CTRL_REG1: 0x{:02x}".format(lis3dh.ctrl_reg1))

print("CTRL_REG2: 0x{:02x}".format(lis3dh.ctrl_reg2))
print("CTRL_REG4: 0x{:02x}".format(lis3dh.ctrl_reg4))
print("CTRL_REG5: 0x{:02x}".format(lis3dh.ctrl_reg5))
print("Data rate: ",lis3dh.print_rate(lis3dh.data_rate))
print("FIFO control register: 0x{:02x}".format(lis3dh.fifo_ctrl_reg))

print("Fifo no of samples: {:d}".format(lis3dh.fifo_no_of_samples))
lis3dh.clear_fifo()
print("status_reg: 0x{:02x}".format(lis3dh.status))

#  enable all axes, normal mode
lis3dh.all_axis_enable = True

while True:
    if not lis3dh.fifo_empty :
        if lis3dh.zyx_overrun :
            print("Overrun error")
            lis3dh.clear_fifo()    
        else:
            accel=lis3dh.accel_raw
            print("accel_x: {:d}, accel_y: {:d}, accel_z: {:d}".format(accel[0],accel[1],accel[2]))
    else :
        sleep_ms(1)
