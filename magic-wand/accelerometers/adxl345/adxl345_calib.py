from machine import Pin,I2C
from micropython import const
from utime import sleep_ms, sleep
from micropython import const
import sys

from adxl345_const import *
from adxl345 import ADXL345

adxl345 = ADXL345(debug=False)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 25 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_25)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
adxl345.setMeasure(False)
adxl345.clearFIFO()
adxl345.setFIFOMode(BYPASS)
adxl345.setMeasure(True)

x_goal = 0
y_goal = 0
z_goal = -256
# set offsets to 0
x_offset = 0
y_offset = 0
z_offset = 0
x_done = False
y_done = False
z_done = False


trash = adxl345.getAccelerometerData()
while True:
    cnt = 0
    adxl345.setXOffset(x_offset)
    adxl345.setYOffset(y_offset)
    adxl345.setZOffset(z_offset)
    if adxl345.getDataReadySource():
        data = adxl345.getAccelerometerData()
        print("x_offset: {:d} x: {:d} y_offset: {:d} y: {:d} z_offset: {:d} z: {:d} ".format(
            x_offset, data[0],y_offset,data[1],z_offset,data[2]))
        if x_done and y_done and z_done:
            print("Done, x_offset =  {:d}, y_offset = {:d} z_offset = {:d}".format(x_offset,y_offset,z_offset))
            break
        if data[0] == x_goal:
            x_done = True
        if not x_done:
            if data[0] > x_goal:
                x_offset -= 1
            elif data[0] < x_goal:
                x_offset += 1
        if data[1] == y_goal:
            y_done = True
        if not y_done:
            if data[1] > y_goal:
                y_offset -= 1
            elif data[1] < y_goal:
                y_offset += 1

        if data[2] == z_goal:
            z_done = True
        if not z_done:
            if data[2] > z_goal:
                z_offset -= 1
            elif data[2] < z_goal:
                z_offset += 1
    else :
        cnt += 1
    if cnt > 1000:
        print("No data seen! Giving up ...")
        sys.exit()
        
