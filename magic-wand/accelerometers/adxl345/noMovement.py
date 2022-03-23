# noMovement.py: Initializes the adxl345 Accelerometer and reads the acceleration
# on the 3 axis during 5 s, when the device is not moved
# Copyright (c) U. Raich Feb. 2022
# This program is part of a course on machine learning at the University of Cape Coast,Ghana
# It is released under the MIT license
#

from machine import Pin,I2C
from micropython import const
from utime import sleep_ms,ticks_ms
from micropython import const

from adxl345_const import *
from adxl345 import ADXL345

adxl345 = ADXL345(debug=False)

AX = const(0)
AY = const(1)
AZ = const(2)
LOOPS = const(100)
AVERAGE = const(10)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 800 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_100)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
# Set the measure bit to start measurement
adxl345.setMeasure(1)
# Set the measure bit to start measurement
adxl345.setMeasure(1)

# get the offsets    
sum = [0]*3
offsets = [None]*3

# Clear the offset registers
adxl345.setXOffset(0)
adxl345.setYOffset(0)
adxl345.setZOffset(0)

# Calibrate
# Get the average offset values
print("Calibrating...")
for i in range(LOOPS):
    accel = adxl345.getAccelerometerData()
    # print("accel x: {:04x}, y: {:04x}, z: {:04x}".format(accel[AX],
    #                                                       accel[AY],
    #                                                       accel[AZ])) 

    sum[AX] += accel[AX]
    sum[AY] += accel[AY]
    sum[AZ] += accel[AZ]
    
for i in range(AX,AZ+1):
    offsets[i] = -round(sum[i]/(4*LOOPS))
    
print("offsets: x: {:02x}, y: {:02x}, z: {:02x}".format(offsets[AX]&0xff,
                                                        offsets[AY]&0xff,
                                                        offsets[AZ]&0xff)) 
adxl345.setXOffset(offsets[AX])
adxl345.setYOffset(offsets[AY])
adxl345.setZOffset(offsets[AZ])

# Read accel values for 5s. Do not move the accelerometer during this time
print("Starting measurement")
print("Data ready: {}".format(adxl345.getDataReady()))
startTime = ticks_ms()
data = [0]*25*3*5
for i in range(5*25):
    if adxl345.getDataReady():
        accel = adxl345.getAccelerometerData()
        data[3*i+AX] = accel[AX]
        data[3*i+AY] = accel[AY]
        data[3*i+AZ] = accel[AZ]

duration = (ticks_ms() - startTime)/1000
print("Duration of measurement: {:.2f}s".format(duration))
print("Ready, saving the data to accel.dat")

f = open("accel.dat","w")
for i in range(25*5):
    f.write("{:04x}, {:04x}, {:04x}\n".format(data[3*i+AX],data[3*i+AY],data[3*i+AZ]))
f.close()
print("Done")
