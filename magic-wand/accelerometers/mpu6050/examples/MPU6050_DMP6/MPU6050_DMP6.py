# 
# I2C device class (I2Cdev) demonstration Arduino sketch for MPU6050 class using DMP (MotionApps v2.0)
# 6/21/2012 by Jeff Rowberg <jeff@rowberg.net>
# Updates should (hopefully) always be available at https:#github.com/jrowberg/i2cdevlib
#
# Changelog:
#      2019-07-08 - Added Auto Calibration and offset generator
#		   - and altered FIFO retrieval sequence to avoid using blocking code
#      2016-04-18 - Eliminated a potential infinite loop
#      2013-05-08 - added seamless Fastwire support
#                 - added note about gyro calibration
#      2012-06-21 - added note about Arduino 1.0.1 + Leonardo compatibility error
#      2012-06-20 - improved FIFO overflow handling and simplified read process
#      2012-06-19 - completely rearranged DMP initialization code and simplification
#      2012-06-13 - pull gyro and accel data from FIFO packet instead of reading directly
#      2012-06-09 - fix broken FIFO read sequence and change interrupt detection to RISING
#      2012-06-05 - add gravity-compensated initial reference frame acceleration output
#                 - add 3D math helper file to DMP6 example sketch
#                 - add Euler output and Yaw/Pitch/Roll output formats
#      2012-06-04 - remove accel offset clearing for better results (thanks Sungon Lee)
#      2012-06-01 - fixed gyro sensitivity to be 2000 deg/sec instead of 250
#      2012-05-30 - basic DMP initialization working

'''
============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2012 Jeff Rowberg

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

'''
   =========================================================================
   NOTE: In addition to connection 3.3v, GND, SDA, and SCL, this sketch
   depends on the MPU-6050's INT pin being connected to the Arduino's
   external interrupt #0 pin. On the Arduino Uno and Mega 2560, this is
   digital I/O pin 2.
   ========================================================================= */

   =========================================================================
   NOTE: Arduino v1.0.1 with the Leonardo board generates a compile error
   when using Serial.write(buf, len). The Teapot output uses this method.
   The solution requires a modification to the Arduino USBAPI.h file, which
   is fortunately simple, but annoying. This will be fixed in the next IDE
   release. For more info, see these links:

   http://arduino.cc/forum/index.php/topic,109987.0.html
   http://code.google.com/p/arduino/issues/detail?id=958
   ========================================================================= */
'''


#  uncomment "OUTPUT_READABLE_QUATERNION" if you want to see the actual
#  quaternion components in a [w, x, y, z] format (not best for parsing
#  on a remote host such as Processing or something though)
# OUTPUT_READABLE_QUATERNION = True

#  uncomment "OUTPUT_READABLE_EULER" if you want to see Euler angles
#  (in degrees) calculated from the quaternions coming from the FIFO.
#  Note that Euler angles suffer from gimbal lock (for more info, see
#  http://en.wikipedia.org/wiki/Gimbal_lock)
# OUTPUT_READABLE_EULER = True

// uncomment "OUTPUT_READABLE_YAWPITCHROLL" if you want to see the yaw/
// pitch/roll angles (in degrees) calculated from the quaternions coming
// from the FIFO. Note this also requires gravity vector calculations.
// Also note that yaw/pitch/roll angles suffer from gimbal lock (for
// more info, see: http://en.wikipedia.org/wiki/Gimbal_lock)
#define OUTPUT_READABLE_YAWPITCHROLL

# uncomment "OUTPUT_READABLE_REALACCEL" if you want to see acceleration
# components with gravity removed. This acceleration reference frame is
# not compensated for orientation, so +X is always +X according to the
# sensor, just without the effects of gravity. If you want acceleration
# compensated for orientation, us OUTPUT_READABLE_WORLDACCEL instead.
# OUTPUT_READABLE_REALACCEL = True

# uncomment "OUTPUT_READABLE_WORLDACCEL" if you want to see acceleration
# components with gravity removed and adjusted for the world frame of
# reference (yaw is relative to initial orientation, since no magnetometer
# is present in this case). Could be quite handy in some cases.
#OUTPUT_READABLE_WORLDACCEL = True

# uncomment "OUTPUT_TEAPOT" if you want output that matches the
# format used for the InvenSense teapot demo
# OUTPUT_TEAPOT = True

led = Pin(19,Pin.OUT)
motionInt = Pin(26,Pin.IN,Pin.PULL_UP)

blinkState = False;

# MPU control/status vars
dmpReady = False        # set true if DMP init was successful
#uint8_t mpuIntStatus;   # holds actual interrupt status byte from MPU
#uint8_t devStatus;      # return status after each device operation (0 = success, !0 = error)
#uint16_t packetSize;    # expected DMP packet size (default is 42 bytes)
#uint16_t fifoCount;     # count of all bytes currently in FIFO
#uint8_t fifoBuffer[64]; # FIFO storage buffer

# orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// packet structure for InvenSense teapot demo
uint8_t teapotPacket[14] = { '$', 0x02, 0,0, 0,0, 0,0, 0,0, 0x00, 0x00, '\r', '\n' };



// ================================================================
// ===               INTERRUPT DETECTION ROUTINE                ===
// ================================================================

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}



# ================================================================
# ===                      INITIAL SETUP                       ===
# ================================================================

# i2c bus is initialized in the MPU6050 class

# initialize device
print("Initializing I2C devices...");
mpu = MPU6050(debug=True)
# mpu = MPU6050()

# Reset the mpu6050 and wait 50 ms for the device to come up again
# print("Reset device")
# accelgyro.reset()
# sleep_ms(50)

# verify connection
print("Testing device connections...")
if mpu.testConnection():
    print("MPU6050 connection successful")
else:
    print("MPU6050 connection failed")
    sys.exit()
    
print("Device ID: 0x{:02x}".format(mpu.getDeviceID()))

# load and configure the DMP
# Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize()

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788); // 1688 factory default for my test chip

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // Calibration Time: generate offsets and calibrate our MPU6050
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.PrintActiveOffsets();
        // turn on the DMP, now that it's ready
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // enable Arduino interrupt detection
        Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
        Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
        Serial.println(F(")..."));
        attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }

    // configure LED for output
    pinMode(LED_PIN, OUTPUT);
}



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
    // read a packet from FIFO
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        #ifdef OUTPUT_READABLE_QUATERNION
            // display quaternion values in easy matrix form: w x y z
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            Serial.print("quat\t");
            Serial.print(q.w);
            Serial.print("\t");
            Serial.print(q.x);
            Serial.print("\t");
            Serial.print(q.y);
            Serial.print("\t");
            Serial.println(q.z);
        #endif

        #ifdef OUTPUT_READABLE_EULER
            // display Euler angles in degrees
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetEuler(euler, &q);
            Serial.print("euler\t");
            Serial.print(euler[0] * 180/M_PI);
            Serial.print("\t");
            Serial.print(euler[1] * 180/M_PI);
            Serial.print("\t");
            Serial.println(euler[2] * 180/M_PI);
        #endif

        #ifdef OUTPUT_READABLE_YAWPITCHROLL
            // display Euler angles in degrees
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
            Serial.print("ypr\t");
            Serial.print(ypr[0] * 180/M_PI);
            Serial.print("\t");
            Serial.print(ypr[1] * 180/M_PI);
            Serial.print("\t");
            Serial.println(ypr[2] * 180/M_PI);
        #endif

        #ifdef OUTPUT_READABLE_REALACCEL
            // display real acceleration, adjusted to remove gravity
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetAccel(&aa, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
            Serial.print("areal\t");
            Serial.print(aaReal.x);
            Serial.print("\t");
            Serial.print(aaReal.y);
            Serial.print("\t");
            Serial.println(aaReal.z);
        #endif

        #ifdef OUTPUT_READABLE_WORLDACCEL
            // display initial world-frame acceleration, adjusted to remove gravity
            // and rotated based on known orientation from quaternion
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetAccel(&aa, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
            mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
            Serial.print("aworld\t");
            Serial.print(aaWorld.x);
            Serial.print("\t");
            Serial.print(aaWorld.y);
            Serial.print("\t");
            Serial.println(aaWorld.z);
        #endif
    
        #ifdef OUTPUT_TEAPOT
            // display quaternion values in InvenSense Teapot demo format:
            teapotPacket[2] = fifoBuffer[0];
            teapotPacket[3] = fifoBuffer[1];
            teapotPacket[4] = fifoBuffer[4];
            teapotPacket[5] = fifoBuffer[5];
            teapotPacket[6] = fifoBuffer[8];
            teapotPacket[7] = fifoBuffer[9];
            teapotPacket[8] = fifoBuffer[12];
            teapotPacket[9] = fifoBuffer[13];
            Serial.write(teapotPacket, 14);
            teapotPacket[11]++; // packetCount, loops at 0xFF on purpose
        #endif

        // blink LED to indicate activity
        blinkState = !blinkState;
        digitalWrite(LED_PIN, blinkState);
    }
}