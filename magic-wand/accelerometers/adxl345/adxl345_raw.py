# adxl345_raw.py: Initializes the adxl345 Accelerometer and reads the
# acceleration on the 3 axis
# Copyright (c) U. Raich Feb. 2022
# This program is part of a course on machine learning at the University of Cape Coast,Ghana
# It is released under the MIT license
#

from machine import Pin,I2C
from micropython import const
from utime import sleep_ms
from micropython import const

from adxl345_const import *
from adxl345 import ADXL345
AX = const(0)
AY = const(1)
AZ = const(2)

adxl345 = ADXL345(debug=False)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 800 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_25)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
# set all the offsets to zero
adxl345.setXOffset(0)
adxl345.setYOffset(0)
adxl345.setZOffset(0)
# Set the measure bit to start measurement
adxl345.setMeasure(True)

while True:
    if adxl345.getDataReadySource():
        accel = adxl345.getAccelerometerData()
        print("accel x: {:d}, y: {:d}, z: {:d}".format(
            accel[AX],accel[AY],accel[AZ])) 
        
