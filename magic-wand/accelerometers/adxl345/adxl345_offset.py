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

# set offsets to 0
print("Increasing offset")
for i in range(128):
    adxl345.setXOffset(i)
    adxl345.setYOffset(i)
    adxl345.setZOffset(i)
    cnt = 0
    while True:
        if adxl345.getDataReadySource():
            data = adxl345.getAccelerometerData()
            print("offset: {:d} x: {:d} y: {:d} z: {:d}".format(i, data[0],data[1],data[2]))
            break
        else :
            cnt += 1
        if cnt > 1000:
            print("No data seen! Giving up ...")
            sys.exit()
        
