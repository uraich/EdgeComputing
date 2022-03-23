# adxl345FIFO.py: Initializes the adxl345 Accelerometer and reads the acceleration
# on the 3 axis using the FIFO
# Copyright (c) U. Raich March 2022
# This program is part of a course on machine learning at the University of Cape Coast,Ghana
# It is released under the MIT license
#

from machine import Pin,I2C
from micropython import const
from utime import sleep_ms, sleep
from micropython import const

from adxl345_const import *
from adxl345 import ADXL345
import random

adxl345 = ADXL345(debug=False)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 25 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_25)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
# set FIFO mode to "FIFO"
adxl345.setFIFOMode(MODE_FIFO)
# set the watermark to 1
adxl345.setSamples(1)
# make sure the fifo is empty
adxl345.clearFIFO()
# start the measurement
adxl345.setMeasure(True)

print("Reading data from fifo")

while True:
    # data.append(adxl345.getFIFO_Data())
    data = adxl345.getFIFO_Data()
    if data:
        print("x: {:d} y: {:d} z: {:d}".format(data[0],data[1],data[2]))

