# readAccel.py: Initializes the adxl345 Accelerometer and reads the acceleration
# on the 3 axis
# Copyright (c) U. Raich Feb. 2022
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

# define the interrupt pins
int1 = Pin(19,Pin.IN)
int2 = Pin(18,Pin.IN)

def callback(source):
    status = adxl345.getInterruptSource() 
    if source == int1:
        # read the INT_SOURCE register to see if activity of inactivity has been detected
        print("INT_source: 0x{:02x}".format(status))
        print("activity: 0x{:02x}, inactivity: 0x{:02x}".format(1<<ACTIVITY,1<<INACTIVITY))
        if status & (1 << ACTIVITY):
            print("activity")
        elif status & (1 << INACTIVITY):
            print("inactivity")

        print("watermark: 0x{:02x}, overrun: 0x{:02x}".format(1<<WATERMARK,1<<OVERRUN))
        print("fifo status: 0x{:02x}".format(adxl345.getFIFO_Status()))
        if status & (1<<OVERRUN):
           print("!!! Overrun error !!!")
        if status & (1<<WATERMARK):
            print("Watermark")
        
adxl345 = ADXL345(debug=False)
# int 1 is used for activity / inactivity
int1.irq(trigger=Pin.IRQ_RISING, handler = callback)
# int 2 controls the FIFO
int2.irq(trigger=Pin.IRQ_RISING, handler = callback)

AX = const(0)
AY = const(1)
AZ = const(2)
LOOPS = const(100)
AVERAGE = const(10)

types = {0: "zero",
         1: "one",
         2: "two",
         3: "three",
         4: "four",
         5: "five",
         6: "six",
         7: "seven",
         8: "eight",
         9: "nine"}

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 100 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_100)
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

print("ACT_INACT register: 0x{:02x}".format(adxl345.getAct_InactControl()))

# Set the activity and inactivity thresholds
adxl345.setActivityThreshold(50)
adxl345.setInactivityThreshold(50)
adxl345.setInactivityTime(5)

# Define the interrupt mapping
adxl345.setInterruptMapping(0)
adxl345.setWatermarkMapping(1)
adxl345.setOverrunMapping(1)

# adxl.setFiFoMode
adxl345.setFiFoMode(FIFO_MODE)
adxl345.setSamples(16)        # watermark interrupt is triggered when 16 samples are in the FIFO

# read number of samples in the FIFO
noOfSamples = adxl345.getFIFO_Entries()
print("{:d} samples found in FIFO".format(noOfSamples))

# Clear the FIFO
for _ in range(noOfSamples):
    adxl345.getAccelerometerData()

# read number of samples in the FIFO
noOfSamples = adxl345.getFIFO_Entries()
print("{:d} samples found in FIFO".format(noOfSamples))
    
# enable the interrupts
adxl345.setActivityIntEnable(True)
adxl345.setInactivityIntEnable(True)
adxl345.setOverrunIntEnable(True)
adxl345.setWatermarkIntEnable(True)

adxl345.setActXEnable(True)
adxl345.setActYEnable(True)
adxl345.setActZEnable(True)
adxl345.setInactXEnable(True)
adxl345.setInactYEnable(True)
adxl345.setInactZEnable(True)

# get the INT_ENABLE register content
print("Interrupt enable register: 0x{:02x}".format(
    adxl345.getInterruptEnable()))

while True:
    pass

    

