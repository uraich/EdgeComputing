# readAccel.py: Initializes the adxl345 Accelerometer and reads the acceleration
# on the 3 axis
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

adxl345 = ADXL345(debug=False)

AX = const(0)
AY = const(1)
AZ = const(2)
LOOPS = const(100)
AVERAGE = const(10)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 800 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_800)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
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

# Read the INT_SOURCE register twice to make sure all bits are reset

print("INT_SOURCE register: 0x{:02x}".format(adxl345.getInterruptSource()))
print("INT_SOURCE register: 0x{:02x}".format(adxl345.getInterruptSource()))

adxl345.setActXEnable(True)
adxl345.setActYEnable(True)
adxl345.setActZEnable(True)
adxl345.setInactXEnable(True)
adxl345.setInactYEnable(True)
adxl345.setInactZEnable(True)

print("ACT_INACT register: 0x{:02x}".format(adxl345.getAct_InactControl()))
# Set the activity and inactivity thresholds
adxl345.setActivityThreshold(50)
adxl345.setInactivityThreshold(50)
adxl345.setInactivityTime(0)

adxl345.setActivityIntEnable(True)
adxl345.setInactivityIntEnable(True)

# get the INT_ENABLE register content
print("Interrupt enable register: 0x{:02x}".format(
    adxl345.getInterruptEnable()))

# adxl345.setDebug(True)
# while True:
    # print("activity: ",adxl345.getActivitySource())
    # print("inactivity: ",adxl345.getInactivitySource())
# Set the interrupt enable 
# Read the activity bit in the INT_SOURCE register
activityFlag = False

# Now read the acceleration values

print("Waiting for activity")

while True:
    if activityFlag:
        for i in range(AVERAGE):
            sum = [0]*3
            accel = adxl345.getAccelerometerData()
            for j in range(AX,AZ+1):
                sum[AX] += accel[AX]
                sum[AY] += accel[AY]
                sum[AZ] += accel[AZ]
                
        print("accel x: {:.2f}, y: {:.2f}, z: {:.2f}".format(sum[AX]/AVERAGE,
                                                             sum[AY]/AVERAGE,
                                                             sum[AZ]/AVERAGE))
        if adxl345.getInactivitySource() :
            print("Inactivity seen")
            activityFlag = False
        
    else:
        # print("Interrupt source register: 0x{:02x}".format(adxl345.getInterruptSource()))
        if adxl345.getActivitySource() :
            print("Activity seen")
            activityFlag = True
    

    

