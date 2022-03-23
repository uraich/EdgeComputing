import sys
import math
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

# i2c bus is initialized in the MPU6050 class

# initialize device
print("Initializing I2C devices...");
# accelgyro = MPU6050(debug=True)
accelgyro = MPU6050()

# Reset the mpu6050 and wait 50 ms for the device to come up again
# print("Reset device")
# accelgyro.reset()
# sleep_ms(50)

debug = True
motionInt = Pin(26,Pin.IN,Pin.PULL_UP)

BUTTON_PIN_BITMASK = const(0x200000000)
RAD_TO_DEG = 360.0/(2*math.pi)

minVal=265
maxVal=402

# initialize device
# print("Initializing I2C devices...")
# accelgyro = MPU6050()
# verify connection
print("Testing device connections...")
if accelgyro.testConnection():
    print("MPU6050 connection successful")
else:
    print("MPU6050 connection failed")
    sys.exit()

# accelgyro.setTempSensorEnabled(false);
  
# Set up zero motion
'''
Get accelerometer power-on delay.
The accelerometer data path provides samples to the sensor registers, Motion
detection, Zero Motion detection, and Free Fall detection modules. The
signal path contains filters which must be flushed on wake-up with new
samples before the detection modules begin operations. The default wake-up
delay, of 4ms can be lengthened by up to 3ms. This additional delay is
specified in ACCEL_ON_DELAY in units of 1 LSB = 1 ms. The user may select
any value above zero unless instructed otherwise by InvenSense. Please refer
to Section 8 of the MPU-6000/MPU-6050 Product Specification document for
further information regarding the detection modules.
@return Current accelerometer power-on delay
@see MPU60X0_RA_MOT_DETECT_CTRL
@see MPU60X0_DETECT_ACCEL_ON_DELAY_BIT
'''
accelgyro.setAccelerometerPowerOnDelay(3)


'''!
Get Zero Motion Detection interrupt enabled status.
Will be set 0 for disabled, 1 for enabled.
@return Current interrupt enabled status
@see MPU60X0_RA_INT_ENABLE
@see MPU60X0_INTERRUPT_ZMOT_BIT
'''
accelgyro.setIntZeroMotionEnabled(True)
if debug :
    print("INT_ENABLE register: 0x{:02x}".format(accelgyro.getIntEnabled()))

'''!
Get the high-pass filter configuration.
The DHPF is a filter module in the path leading to motion detectors (Free
Fall, Motion threshold, and Zero Motion). The high pass filter output is not
available to the data registers (see Figure in Section 8 of the MPU-6000/
MPU-6050 Product Specification document).

The high pass filter has three modes:
   Reset: The filter output settles to zero within one sample. This
          effectively disables the high pass filter. This mode may be toggled
          to quickly settle the filter.

   On:    The high pass filter will pass signals above the cut off frequency.

   Hold:  When triggered, the filter holds the present sample. The filter
          output will be the difference between the input sample and the held
          sample.

ACCEL_HPF | Filter Mode | Cut-off Frequency
----------+-------------+------------------
0         | Reset       | None
1         | On          | 5Hz
2         | On          | 2.5Hz
3         | On          | 1.25Hz
4         | On          | 0.63Hz
7         | Hold        | None
</pre>

@return Current high-pass filter configuration
@see MPU60X0_DHPF_RESET
@see MPU60X0_RA_ACCEL_CONFIG
'''
if debug:
  print("Setting DHPF bandwidth to 5Hz...")

accelgyro.setDHPFMode(1)
if debug:
    print("Readback DHPF mode: 0x{:02x}".format(accelgyro.getDHPFMode()))

'''!
Set the full scale
'''
accelgyro.setFullScaleAccelRange(MPU6050_ACCEL_FS_8)
if debug:
    print("Readback full range: 0x{:02x}".format(accelgyro.getFullScaleAccelRange()))
    print("Readback ACCEL_CONFIG register: 0x{:02x}".format(accelgyro.getAccelConfig()))
    
'''!
Get motion detection event acceleration threshold.
This register configures the detection threshold for Motion interrupt
generation. The unit of MOT_THR is 1LSB = 2mg. Motion is detected when the
absolute value of any of the accelerometer measurements exceeds this Motion
detection threshold. This condition increments the Motion detection duration
counter (Register 32). The Motion detection interrupt is triggered when the
Motion Detection counter reaches the time count specified in MOT_DUR
(Register 32).

The Motion interrupt will indicate the axis and polarity of detected motion
in MOT_DETECT_STATUS (Register 97).

For more details on the Motion detection interrupt, see Section 8.3 of the
MPU-6000/MPU-6050 Product Specification document as well as Registers 56 and
58 of this document.

@return Current motion detection acceleration threshold value (LSB = 2mg)
@see MPU60X0_RA_MOT_THR
'''
if debug:
    print("Setting motion detection threshold to 16...")
accelgyro.setMotionDetectionThreshold(16)
if debug:
    print("Reading back motion detection threshold: {:d}".format(
        accelgyro.getMotionDetectionThreshold()))

'''!
Get zero motion detection event acceleration threshold.
This register configures the detection threshold for Zero Motion interrupt
generation. The unit of ZRMOT_THR is 1LSB = 2mg. Zero Motion is detected when
the absolute value of the accelerometer measurements for the 3 axes are each
less than the detection threshold. This condition increments the Zero Motion
duration counter (Register 34). The Zero Motion interrupt is triggered when
the Zero Motion duration counter reaches the time count specified in
ZRMOT_DUR (Register 34).

Unlike Free Fall or Motion detection, Zero Motion detection triggers an
interrupt both when Zero Motion is first detected and when Zero Motion is no
longer detected.

When a zero motion event is detected, a Zero Motion Status will be indicated
in the MOT_DETECT_STATUS register (Register 97). When a motion-to-zero-motion
condition is detected, the status bit is set to 1. When a zero-motion-to-
motion condition is detected, the status bit is set to 0.

For more details on the Zero Motion detection interrupt, see Section 8.4 of
the MPU-6000/MPU-6050 Product Specification document as well as Registers 56
and 58 of this document.

@return Current zero motion detection acceleration threshold value (LSB = 2mg)
@see MPU60X0_RA_ZRMOT_THR
'''
if debug:
    print("Setting zero-motion detection threshold to 156...")
accelgyro.setZeroMotionDetectionThreshold(156)
if debug:
    print("Reading back zero-motion detection threshold: {:d}".format(
        accelgyro.getZeroMotionDetectionThreshold()))

'''!
Get motion detection event duration threshold.
This register configures the duration counter threshold for Motion interrupt
generation. The duration counter ticks at 1 kHz, therefore MOT_DUR has a unit
of 1LSB = 1ms. The Motion detection duration counter increments when the
absolute value of any of the accelerometer measurements exceeds the Motion
detection threshold (Register 31). The Motion detection interrupt is
triggered when the Motion detection counter reaches the time count specified
in this register.

For more details on the Motion detection interrupt, see Section 8.3 of the
MPU-6000/MPU-6050 Product Specification document.

@return Current motion detection duration threshold value (LSB = 1ms)
@see MPU60X0_RA_MOT_DUR
'''
if debug:
    print("Setting motion detection duration to 40...")
accelgyro.setMotionDetectionDuration(2)


'''!
Get zero motion detection event duration threshold.
This register configures the duration counter threshold for Zero Motion
interrupt generation. The duration counter ticks at 16 Hz, therefore
ZRMOT_DUR has a unit of 1 LSB = 64 ms. The Zero Motion duration counter
increments while the absolute value of the accelerometer measurements are
each less than the detection threshold (Register 33). The Zero Motion
interrupt is triggered when the Zero Motion duration counter reaches the time
count specified in this register.

For more details on the Zero Motion detection interrupt, see Section 8.4 of
the MPU-6000/MPU-6050 Product Specification document, as well as Registers 56
and 58 of this document.

@return Current zero motion detection duration threshold value (LSB = 64ms)
@see MPU60X0_RA_ZRMOT_DUR
'''
if debug:
    print("Setting zero-motion detection duration to 0...");
accelgyro.setZeroMotionDetectionDuration(64)

if debug:
    print("Reading back zero-motion detection duration: {:d}".format(
    accelgyro.getZeroMotionDetectionDuration()))
    
for i in range(1):
    # read raw accel/gyro measurements from device
    if debug:
        print("Getting raw accwl/gyro measurements")
    motion = accelgyro.getMotion6()
    if debug:
        print("Motion, ax: {:d}, ay: {:d}, az: {:d}, gx: {:d}, gy: {:d}, gz: {:d}".format(
            motion[0],motion[1],motion[2],motion[3],motion[4],motion[5]))

print("Getting Motion indicators, count and threshold")

print("Motion status: 0x{:02x}".format(accelgyro.getMotionStatus()))

XnegMD = accelgyro.getXNegMotionDetected()
XposMD = accelgyro.getXPosMotionDetected()
YnegMD = accelgyro.getYNegMotionDetected()
YposMD = accelgyro.getYPosMotionDetected()
ZnegMD = accelgyro.getZNegMotionDetected()
ZposMD = accelgyro.getZPosMotionDetected()

zero_detect = accelgyro.getIntMotionStatus()
threshold = accelgyro.getZeroMotionDetectionThreshold()

print("Got to count")
count = accelgyro.getMotionDetectionCounterDecrement()

'''!
Get current internal temperature.
  @return Temperature reading in 16-bit 2's complement format
  @see MPU60X0_RA_TEMP_OUT_H
'''
if debug:
    print("Getting Die Temperature")
temp = accelgyro.getTemperature() / 340. + 36.53
print("Temperature: {:.2f}°C".format(temp))

'''!
The accelerometer and gyroscope measurements are explained in the MPU-6050
datasheet in the GYRO_CONFIG and ACCEL_CONFIG register descriptions (sections 4.4
and 4.5 on pages 14 and 15). The scale of each depends on the sensitivity settings
chosen, which can be one of +/- 2, 4, 8, or 16g for the accelerometer and one of
+/- 250, 500, 1000, or 2000 deg/sec for the gyroscope. The accelerometer produces data
in units of acceleration (distance over time2), and the gyroscope produces data in units
of rotational velocity (rotation distance over time).

The output scale for any setting is [-32768, +32767] for each of the six axes. The default
setting in the I2Cdevlib class is +/- 2g for the accel and +/- 250 deg/sec for the gyro. If
the device is perfectly level and not moving, then:
    X/Y accel axes should read 0
    Z accel axis should read 1g, which is +16384 at a sensitivity of 2g
    X/Y/Z gyro axes should read 0

In reality, the accel axes won't read exactly 0 since it is difficult to be perfectly level
and there is some noise/error, and the gyros will also not read exactly 0 for the same reason
(noise/error).
'''

# these methods (and a few others) are also available
accel = accelgyro.getAcceleration()
ax = accel[0]
ay = accel[1]
az = accel[2]
gyro = accelgyro.getRotation()
gx = gyro[0]
gy = gyro[1]
gz = gyro[2]


print("Acceleration: ax: {:.2f}g, ax: {:.2f}g, az: {:.2f}g".format(ax/16384.,ay/16384.,az/16384.))
print("Gyroscope:    gx: {:.2f} , gy: {:.2f} , gz: {:.2f}".format(gx/131.072,gx/131.072,gx/131.072))

print("zero_detect {:02x}, XnegMD {:02x}, XposMD {:02x}".format(zero_detect,XnegMD,XposMD))

xAng = accelgyro.map(ax,minVal,maxVal,-90,90)
yAng = accelgyro.map(ay,minVal,maxVal,-90,90) 
zAng = accelgyro.map(az,minVal,maxVal,-90,90)

x= RAD_TO_DEG * (math.atan2(-yAng, -zAng)+math.pi)
y= RAD_TO_DEG * (math.atan2(-xAng, -zAng)+math.pi) 
z= RAD_TO_DEG * (math.atan2(-yAng, -xAng)+math.pi)

print("AngleX= {:.2f}, AngleY: {:.2f}, AngleZ: {:.2f}".format(x,y,z))

# display tab-separated accel/gyro x/y/z values

print("a/g:\t{:.2f}\t{:02f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}".format(
    ax/16384.,ay/16384.,az/16384.,gx/131.072,gy/131.072,gz/131.072))

print("ZeroMotion(97):\t{:.2f}\tCount:\t{:-2f}".format(zero_detect,count))
print("{:.2f}\t{:02f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}".format(XnegMD,XposMD,YnegMD,YposMD,ZnegMD,ZposMD))

