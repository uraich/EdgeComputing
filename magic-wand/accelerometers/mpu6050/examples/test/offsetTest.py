# reads accelx and increased the offset
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

# uncomment "OUTPUT_READABLE_ACCELGYRO" if you want to see a tab-separated
# list of the accel X/Y/Z and then gyro X/Y/Z values in decimal. Easy to read,
# not so easy to parse, and slow(er) over UART.
OUTPUT_READABLE_ACCELGYRO = True

# uncomment "OUTPUT_BINARY_ACCELGYRO" to send all 6 axes of data as 16-bit
# binary, one right after the other. This is very fast (as fast as possible
# without compression or data loss), and easy to parse, but impossible to read
# for a human.
# OUTPUT_BINARY_ACCELGYRO = True

led = Pin(19,Pin.OUT)
blinkState = False

# i2c bus is initialized in the MPU6050 class

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

# use the code below to change accel/gyro offset values
print("device ID: 0x{:02x}".format(accelgyro.getDeviceID()))
for i in range(100):
    accelgyro.setYAccelOffset(-20*i)
    offs = accelgyro.getYAccelOffset()
    sleep_ms(1)
    ay = accelgyro.getAccelerationY()
    print("Offset: {:d} {:d} measured acceleration {:d}".format(-20*i,offs,ay))
