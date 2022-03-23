# reads accelx for different full scales
import sys
from utime import sleep_ms 
from machine import Pin,I2C 
from MPU6050_const import *
from MPU6050 import MPU6050

# initialize device
print("Initializing I2C devices...");
# accelgyro = MPU6050(debug=True)
accelgyro = MPU6050()

# verify connection
print("Testing device connections...")
if accelgyro.testConnection():
    print("MPU6050 connection successful")
else:
    print("MPU6050 connection failed")
    sys.exit()

# get the device ID
print("device ID: 0x{:02x}".format(accelgyro.getDeviceID()))

# set the accel offset to zero
accelgyro.setXAccelOffset(0)

fs = { 0: "2g", 1: "4g", 2: "8g", 3: "16g"}

for i in range(4):
    # set the accel full scale
    print ("setting the full scale to ",fs[i])
    accelgyro.setFullScaleAccelRange(i)
    sleep_ms(1)
    print("Full scale set to ",fs[accelgyro.getFullScaleAccelRange()])

    # Read the x acceleration
    print(" X acceleration at 2G full scale: 0x{:d}".format(accelgyro.getAccelerationX()))
    sleep_ms(10)


