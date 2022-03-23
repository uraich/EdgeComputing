from machine import Pin,I2C
from micropython import const
from utime import sleep_ms, sleep
from micropython import const

from adxl345_const import *
from adxl345 import ADXL345

adxl345 = ADXL345(debug=False)

# set low power to 0 to use normal operation
adxl345.setLowPower(0)
# set rate to 25 Hz (max for 400 kHz I2C bus frequency)
adxl345.setDataRate(RATE_25)
# Set the range to 2g
adxl345.setRange(ACCEL_2G)
# start calibration
adxl345.calibrate()
