# readAccelFIFO.py: Initializes the adxl345 Accelerometer and reads the acceleration
# on the 3 axis using the 32 slot fifo
# Copyright (c) U. Raich March 2022
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
# set rate to 25 Hz (max frequency without risking FIFO overflow)
adxl345.setDataRate(RATE_25)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
# Set the measure bit to start measurement
adxl345.setMeasure(False)

# calibrate
print("Calibrating ...")
adxl345.calibrate()

# Read the INT_SOURCE register twice to make sure all bits are reset

print("INT_SOURCE register: 0x{:02x}".format(adxl345.getInterruptSource()))
print("INT_SOURCE register: 0x{:02x}".format(adxl345.getInterruptSource()))

adxl345.setActXEnable(True)
adxl345.setActYEnable(True)
adxl345.setActZEnable(True)
adxl345.setInactXEnable(True)
adxl345.setInactYEnable(True)
adxl345.setInactZEnable(True)

# enable the FIFO
adxl345.setFIFOMode(MODE_FIFO)
# set the watermark to 1
adxl345.setSamples(1)

print("ACT_INACT register: 0x{:02x}".format(adxl345.getAct_InactControl()))
# Set the activity and inactivity thresholds
adxl345.setActivityThreshold(50)
adxl345.setInactivityThreshold(50)
adxl345.setInactivityTime(2)

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
adxl345.setMeasure(True)
activityFlag = False

# Now read the acceleration values

print("Waiting for activity")

while True:
    if activityFlag:
        accel = adxl345.getFIFO_Data()
        if accel:
            print("accel x: {:.2f}, y: {:.2f}, z: {:.2f}".format(accel[AX],accel[AY],accel[AZ]))

        if adxl345.getInactivitySource() :
            print("Inactivity seen")
            activityFlag = False
        
    else:
        # print("Interrupt source register: 0x{:02x}".format(adxl345.getInterruptSource()))
        if adxl345.getActivitySource() :
            print("Activity seen")
            adxl345.clearFIFO()
            activityFlag = True
    

    

