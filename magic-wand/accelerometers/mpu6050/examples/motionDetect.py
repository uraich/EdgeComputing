# A program to measure gestures to be input as features into a machine learning
# model. It allows to capture data to train the model.
# The program follows the instructions explained in
# https://www.eluke.nl/2016/08/11/how-to-enable-motion-detection-interrupt-on-mpu6050
# This program is part of a course on machine learning prepared for the
# University of Cape Coast, Ghana
#
# Changelog:
#
#      2022-Feb-11 - initial release

# ============================================
'''

Copyright (c) 2022 Uli Raich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
'''
import sys
from utime import sleep_ms 
from machine import Pin,I2C 
from MPU6050_const import *
from MPU6050 import MPU6050

# class default I2C address is 0x68
# specific I2C addresses may be passed as a parameter here
# AD0 low = 0x68 (default for InvenSense evaluation board)
# AD0 high = 0x69

# MPU6050 accelgyro(0x69); // <-- use for AD0 high
# MPU6050 accelgyro(0x68, &Wire1); // <-- use for AD0 low, but 2nd Wire (TWI/I2C) object

led = Pin(19,Pin.OUT)
motionInt = Pin(26,Pin.IN,Pin.PULL_UP)

def motionDetect(source):
    intStatus = accelgyro.getIntStatus()
    print("Interrupt status: {:02x}".format(intStatus))
    if intStatus & (1 << MPU6050_INTERRUPT_MOT_BIT):
        print("Motion detected")
    if intStatus & (1 << MPU6050_INTERRUPT_ZMOT_BIT):
        print("Zero Motion detected")
        
        
blinkState = False

# i2c bus is initialized in the MPU6050 class

# initialize device
print("Initializing I2C devices...");
accelgyro = MPU6050(debug=True)
# accelgyro = MPU6050()

# Reset the mpu6050 and wait 50 ms for the device to come up again
# print("Reset device")
# accelgyro.reset()
# sleep_ms(50)

# verify connection
print("Testing device connections...")
if accelgyro.testConnection():
    print("MPU6050 connection successful")
else:
    print("MPU6050 connection failed")
    sys.exit()
    
print("Device ID: 0x{:02x}".format(accelgyro.getDeviceID()))
accelgyro.setAccelerometerPowerOnDelay(3)

# Reset the signal path
# This should not be necessary since we did a full reset
accelgyro.resetAccelerometerPath()
accelgyro.resetGyroscopePath()
accelgyro.resetTemperaturePath()

# Setup interrupt configuration
accelgyro.setInterruptMode(1)   # active low
accelgyro.setInterruptLatch(1)  # latch until cleared

# Get the state of the interrupt config register
print("Interrupt config register state: 0x{:02x}".format(
    accelgyro.getInterruptConfig()))

# Read back the interrupt configuration and print
int_cfg = accelgyro.getInterruptMode()
print("State of INT_PIN_CFG register (0x37) : {:02x}".format(int_cfg))

# Set the accelerometer full scale
accelgyro.setFullScaleAccelRange(MPU6050_ACCEL_FS_8)
full_scale = accelgyro.getFullScaleAccelRange()
print("Accel full scale read back: 0x{:02x}".format(full_scale))

# Set the digital high pass filter and read it back
accelgyro.setDHPFMode(1) 
print("Digital High Pass Filter (DHPF) mode: 0x{:02x}".format(accelgyro.getDHPFMode()))

# set the accelerrometer config register
print("Setting the accel config register to 9")
accelgyro.setAccelConfig(0x9)
sleep_ms(10)
# read the accelerometer config register
accel_config = accelgyro.getAccelConfig()
print("Accel Config register: 0x{:02x}".format(accel_config))

# use the code below to change accel/gyro offset values
accelgyro.setXAccelOffset(-1082)
accelgyro.setYAccelOffset(-2965)
accelgyro.setZAccelOffset(1256)
accelgyro.setXGyroOffset(76)
accelgyro.setYGyroOffset(39)
accelgyro.setZGyroOffset(12)

print("Updating internal sensor offsets...")
#  -1082    -2968    1256   72,    39	11
print(accelgyro.getXAccelOffset(), end = '')
print("\t",end='') # -1082
print(accelgyro.getYAccelOffset(),end='')
print("\t",end='') # -2968
print(accelgyro.getZAccelOffset(),end='')
print("\t",end='') # 1256
print(accelgyro.getXGyroOffset(),end='')
print("\t",end='') # 72
print(accelgyro.getYGyroOffset(),end='')
print("\t",end='') # 39
print(accelgyro.getZGyroOffset(),end='')
print("\t",end='') # 11
print("")

# Enable the data ready interrupt
accelgyro.setIntDataReadyEnabled(False)
intStatus = accelgyro.getIntStatus()
print("Interrupt status: {:02x}".format(intStatus))
intStatus = accelgyro.getIntStatus()
print("Interrupt status: {:02x}".format(intStatus))
# attach IRQ on D0 (GPIO 26) to motionDetect callback
print("Attach motion detect interrupt to the interrupt handler")
motionInt.irq(trigger=Pin.IRQ_FALLING, handler= motionDetect)

print("Enable the motion detect interrupt")
# enable the motion detect interrupt in the MPU6050
print("Before enabling the interrupt")
accelgyro.setIntMotionEnabled(False)
if accelgyro.getIntMotionEnabled():
    print("Motion detect interrupt is enabled")
else:
    print("Motion detect interrupt is disabled")

print("After ...")
accelgyro.setIntMotionEnabled(True)
if accelgyro.getIntMotionEnabled():
    print("Motion detect interrupt is enabled")
else:
    print("Motion detect interrupt is disabled")

while True:
    # blink LED to indicate activity
    blinkState = not blinkState
    led.value(blinkState)
    sleep_ms(100)


