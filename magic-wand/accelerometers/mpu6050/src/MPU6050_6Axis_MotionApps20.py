# I2Cdev library collection - MPU6050 I2C device class, 6-axis MotionApps 2.0 implementation
# Based on InvenSense MPU-6050 register map document rev. 2.0, 5/19/2011 (RM-MPU-6000A-00)
# 5/20/2013 by Jeff Rowberg <jeff@rowberg.net>
# Updates should (hopefully) always be available at https:#github.com/jrowberg/i2cdevlib
#
# Changelog:
#  2021/09/27 - split implementations out of header files, finally
#  2019/07/08 - merged all DMP Firmware configuration items into the dmpMemory array
#             - Simplified dmpInitialize() to accomidate the dmpmemory array alterations

'''
============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2021 Jeff Rowberg

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

# MotionApps 2.0 DMP implementation, built using the MPU-6050EVB evaluation board
MPU6050_INCLUDE_DMP_MOTIONAPPS20 = True

#include "MPU6050_6Axis_MotionApps20.h"

# Tom Carpenter's conditional PROGMEM code
# http://forum.arduino.cc/index.php?topic=129407.0


#  Source is from the InvenSense MotionApps v2 demo code. Original source is
#  unavailable, unless you happen to be amazing as decompiling binary by
# hand (in which case, please contact me, and I'm totally serious).
#
#  Also, I'd like to offer many, many thanks to Noah Zerkin for all of the
#  DMP reverse-engineering he did to help make this bit of wizardry
#  possible.

# NOTE! Enabling DEBUG adds about 3.3kB to the flash program size.
# Debug output is now working even on ATMega328P MCUs (e.g. Arduino Uno)
# after moving string constants to flash memory storage using the F()
# compiler macro (Arduino IDE 1.0+ required).

from MPU6050 import MPU6050
from MPU6050_const import *

from utime import sleep_ms

MPU6050_DMP_CODE_SIZE       = 1929    # dmpMemory[]
MPU6050_DMP_CONFIG_SIZE     = 192     # dmpConfig[]
MPU6050_DMP_UPDATES_SIZE    = 47      # dmpUpdates[]

'''
/* ================================================================================================ *
 | Default MotionApps v2.0 42-byte FIFO packet structure:                                           |
 |                                                                                                  |
 | [QUAT W][      ][QUAT X][      ][QUAT Y][      ][QUAT Z][      ][GYRO X][      ][GYRO Y][      ] |
 |   0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  |
 |                                                                                                  |
 | [GYRO Z][      ][ACC X ][      ][ACC Y ][      ][ACC Z ][      ][      ]                         |
 |  24  25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41                          |
 * ================================================================================================ */
'''
# this block of memory gets written to the MPU on start-up, and it seems
# to be volatile memory, so it has to be done each time (it only takes ~1
#  second though)

# I Only Changed this by applying all the configuration data and capturing it before startup:
# *** this is a capture of the DMP Firmware after all the messy changes were made so we can just load it


class MPU6050_DMP(MPU6050):
    def __init__(self,debug=False):
        super().__init__(debug=debug)
        # dmpMemory
        banks = [None]*8
        banks[0] = bytearray(b'''\
\xFB\x00\x00\x3E\x00\x0B\x00\x36\x00\x01\x00\x02\x00\x03\x00\x00\
\x00\x65\x00\x54\xFF\xEF\x00\x00\xFA\x80\x00\x0B\x12\x82\x00\x01\
\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x28\x00\x00\xFF\xFF\x45\x81\xFF\xFF\xFA\x72\x00\x00\x00\x00\
\x00\x00\x03\xE8\x00\x00\x00\x01\x00\x01\x7F\xFF\xFF\xFE\x80\x01\
\x00\x1B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x40\x00\x00\x40\x00\x00\x00\x02\xCB\x47\xA2\x20\x00\x00\x00\
\x20\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x60\x00\x00\x00\
\x41\xFF\x00\x00\x00\x00\x0B\x2A\x00\x00\x16\x55\x00\x00\x21\x82\
\xFD\x87\x26\x50\xFD\x80\x00\x00\x00\x1F\x00\x00\x00\x05\x80\x00\
\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\
\x40\x00\x00\x00\x00\x00\x04\x6F\x00\x02\x65\x32\x00\x00\x5E\xC0\
\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\xFB\x8C\x6F\x5D\xFD\x5D\x08\xD9\x00\x7C\x73\x3B\x00\x6C\x12\xCC\
\x32\x00\x13\x9D\x32\x00\xD0\xD6\x32\x00\x08\x00\x40\x00\x01\xF4\
\xFF\xE6\x80\x79\x02\x00\x00\x00\x00\x00\xD0\xD6\x00\x00\x27\x10''')

        banks[1] = bytearray(b'''\
\xFB\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\
\x00\x00\xFA\x36\xFF\xBC\x30\x8E\x00\x05\xFB\xF0\xFF\xD9\x5B\xC8\
\xFF\xD0\x9A\xBE\x00\x00\x10\xA9\xFF\xF4\x1E\xB2\x00\xCE\xBB\xF7\
\x00\x00\x00\x01\x00\x00\x00\x04\x00\x02\x00\x02\x02\x00\x00\x0C\
\xFF\xC2\x80\x00\x00\x01\x80\x00\x00\xCF\x80\x00\x40\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x14\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x09\x23\xA1\x35\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x03\x3F\x68\xB6\x79\x35\x28\xBC\xC6\x7E\xD1\x6C\
\x80\x00\xFF\xFF\x40\x00\x00\x00\x00\x00\xB2\x6A\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\xF0\x00\x00\x00\x30\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\
\x00\x00\x25\x4D\x00\x2F\x70\x6D\x00\x00\x05\xAE\x00\x0C\x02\xD0''')

        banks[2] = bytearray(b'''\
\x00\x00\x00\x00\x00\x65\x00\x54\xFF\xEF\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\x00\x00\x44\x00\x01\x00\x05\x8B\xC1\x00\x00\x01\x00\
\x00\x00\x00\x00\x00\x65\x00\x00\x00\x54\x00\x00\xFF\xEF\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x1B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x1B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00''')

        banks[3] = bytearray(b'''\
\xD8\xDC\xBA\xA2\xF1\xDE\xB2\xB8\xB4\xA8\x81\x91\xF7\x4A\x90\x7F\
\x91\x6A\xF3\xF9\xDB\xA8\xF9\xB0\xBA\xA0\x80\xF2\xCE\x81\xF3\xC2\
\xF1\xC1\xF2\xC3\xF3\xCC\xA2\xB2\x80\xF1\xC6\xD8\x80\xBA\xA7\xDF\
\xDF\xDF\xF2\xA7\xC3\xCB\xC5\xB6\xF0\x87\xA2\x94\x24\x48\x70\x3C\
\x95\x40\x68\x34\x58\x9B\x78\xA2\xF1\x83\x92\x2D\x55\x7D\xD8\xB1\
\xB4\xB8\xA1\xD0\x91\x80\xF2\x70\xF3\x70\xF2\x7C\x80\xA8\xF1\x01\
\xB0\x98\x87\xD9\x43\xD8\x86\xC9\x88\xBA\xA1\xF2\x0E\xB8\x97\x80\
\xF1\xA9\xDF\xDF\xDF\xAA\xDF\xDF\xDF\xF2\xAA\x4C\xCD\x6C\xA9\x0C\
\xC9\x2C\x97\x97\x97\x97\xF1\xA9\x89\x26\x46\x66\xB0\xB4\xBA\x80\
\xAC\xDE\xF2\xCA\xF1\xB2\x8C\x02\xA9\xB6\x98\x00\x89\x0E\x16\x1E\
\xB8\xA9\xB4\x99\x2C\x54\x7C\xB0\x8A\xA8\x96\x36\x56\x76\xF1\xB9\
\xAF\xB4\xB0\x83\xC0\xB8\xA8\x97\x11\xB1\x8F\x98\xB9\xAF\xF0\x24\
\x08\x44\x10\x64\x18\xF1\xA3\x29\x55\x7D\xAF\x83\xB5\x93\xAF\xF0\
\x00\x28\x50\xF1\xA3\x86\x9F\x61\xA6\xDA\xDE\xDF\xD9\xFA\xA3\x86\
\x96\xDB\x31\xA6\xD9\xF8\xDF\xBA\xA6\x8F\xC2\xC5\xC7\xB2\x8C\xC1\
\xB8\xA2\xDF\xDF\xDF\xA3\xDF\xDF\xDF\xD8\xD8\xF1\xB8\xA8\xB2\x86''')

        banks[4] = bytearray(b'''\
\xB4\x98\x0D\x35\x5D\xB8\xAA\x98\xB0\x87\x2D\x35\x3D\xB2\xB6\xBA\
\xAF\x8C\x96\x19\x8F\x9F\xA7\x0E\x16\x1E\xB4\x9A\xB8\xAA\x87\x2C\
\x54\x7C\xB9\xA3\xDE\xDF\xDF\xA3\xB1\x80\xF2\xC4\xCD\xC9\xF1\xB8\
\xA9\xB4\x99\x83\x0D\x35\x5D\x89\xB9\xA3\x2D\x55\x7D\xB5\x93\xA3\
\x0E\x16\x1E\xA9\x2C\x54\x7C\xB8\xB4\xB0\xF1\x97\x83\xA8\x11\x84\
\xA5\x09\x98\xA3\x83\xF0\xDA\x24\x08\x44\x10\x64\x18\xD8\xF1\xA5\
\x29\x55\x7D\xA5\x85\x95\x02\x1A\x2E\x3A\x56\x5A\x40\x48\xF9\xF3\
\xA3\xD9\xF8\xF0\x98\x83\x24\x08\x44\x10\x64\x18\x97\x82\xA8\xF1\
\x11\xF0\x98\xA2\x24\x08\x44\x10\x64\x18\xDA\xF3\xDE\xD8\x83\xA5\
\x94\x01\xD9\xA3\x02\xF1\xA2\xC3\xC5\xC7\xD8\xF1\x84\x92\xA2\x4D\
\xDA\x2A\xD8\x48\x69\xD9\x2A\xD8\x68\x55\xDA\x32\xD8\x50\x71\xD9\
\x32\xD8\x70\x5D\xDA\x3A\xD8\x58\x79\xD9\x3A\xD8\x78\x93\xA3\x4D\
\xDA\x2A\xD8\x48\x69\xD9\x2A\xD8\x68\x55\xDA\x32\xD8\x50\x71\xD9\
\x32\xD8\x70\x5D\xDA\x3A\xD8\x58\x79\xD9\x3A\xD8\x78\xA8\x8A\x9A\
\xF0\x28\x50\x78\x9E\xF3\x88\x18\xF1\x9F\x1D\x98\xA8\xD9\x08\xD8\
\xC8\x9F\x12\x9E\xF3\x15\xA8\xDA\x12\x10\xD8\xF1\xAF\xC8\x97\x87''')

        banks[5] = bytearray(b'''\
\x34\xB5\xB9\x94\xA4\x21\xF3\xD9\x22\xD8\xF2\x2D\xF3\xD9\x2A\xD8\
\xF2\x35\xF3\xD9\x32\xD8\x81\xA4\x60\x60\x61\xD9\x61\xD8\x6C\x68\
\x69\xD9\x69\xD8\x74\x70\x71\xD9\x71\xD8\xB1\xA3\x84\x19\x3D\x5D\
\xA3\x83\x1A\x3E\x5E\x93\x10\x30\x81\x10\x11\xB8\xB0\xAF\x8F\x94\
\xF2\xDA\x3E\xD8\xB4\x9A\xA8\x87\x29\xDA\xF8\xD8\x87\x9A\x35\xDA\
\xF8\xD8\x87\x9A\x3D\xDA\xF8\xD8\xB1\xB9\xA4\x98\x85\x02\x2E\x56\
\xA5\x81\x00\x0C\x14\xA3\x97\xB0\x8A\xF1\x2D\xD9\x28\xD8\x4D\xD9\
\x48\xD8\x6D\xD9\x68\xD8\xB1\x84\x0D\xDA\x0E\xD8\xA3\x29\x83\xDA\
\x2C\x0E\xD8\xA3\x84\x49\x83\xDA\x2C\x4C\x0E\xD8\xB8\xB0\xA8\x8A\
\x9A\xF5\x20\xAA\xDA\xDF\xD8\xA8\x40\xAA\xD0\xDA\xDE\xD8\xA8\x60\
\xAA\xDA\xD0\xDF\xD8\xF1\x97\x86\xA8\x31\x9B\x06\x99\x07\xAB\x97\
\x28\x88\x9B\xF0\x0C\x20\x14\x40\xB8\xB0\xB4\xA8\x8C\x9C\xF0\x04\
\x28\x51\x79\x1D\x30\x14\x38\xB2\x82\xAB\xD0\x98\x2C\x50\x50\x78\
\x78\x9B\xF1\x1A\xB0\xF0\x8A\x9C\xA8\x29\x51\x79\x8B\x29\x51\x79\
\x8A\x24\x70\x59\x8B\x20\x58\x71\x8A\x44\x69\x38\x8B\x39\x40\x68\
\x8A\x64\x48\x31\x8B\x30\x49\x60\xA5\x88\x20\x09\x71\x58\x44\x68''')

        banks[6] = bytearray(b'''\
\x11\x39\x64\x49\x30\x19\xF1\xAC\x00\x2C\x54\x7C\xF0\x8C\xA8\x04\
\x28\x50\x78\xF1\x88\x97\x26\xA8\x59\x98\xAC\x8C\x02\x26\x46\x66\
\xF0\x89\x9C\xA8\x29\x51\x79\x24\x70\x59\x44\x69\x38\x64\x48\x31\
\xA9\x88\x09\x20\x59\x70\xAB\x11\x38\x40\x69\xA8\x19\x31\x48\x60\
\x8C\xA8\x3C\x41\x5C\x20\x7C\x00\xF1\x87\x98\x19\x86\xA8\x6E\x76\
\x7E\xA9\x99\x88\x2D\x55\x7D\x9E\xB9\xA3\x8A\x22\x8A\x6E\x8A\x56\
\x8A\x5E\x9F\xB1\x83\x06\x26\x46\x66\x0E\x2E\x4E\x6E\x9D\xB8\xAD\
\x00\x2C\x54\x7C\xF2\xB1\x8C\xB4\x99\xB9\xA3\x2D\x55\x7D\x81\x91\
\xAC\x38\xAD\x3A\xB5\x83\x91\xAC\x2D\xD9\x28\xD8\x4D\xD9\x48\xD8\
\x6D\xD9\x68\xD8\x8C\x9D\xAE\x29\xD9\x04\xAE\xD8\x51\xD9\x04\xAE\
\xD8\x79\xD9\x04\xD8\x81\xF3\x9D\xAD\x00\x8D\xAE\x19\x81\xAD\xD9\
\x01\xD8\xF2\xAE\xDA\x26\xD8\x8E\x91\x29\x83\xA7\xD9\xAD\xAD\xAD\
\xAD\xF3\x2A\xD8\xD8\xF1\xB0\xAC\x89\x91\x3E\x5E\x76\xF3\xAC\x2E\
\x2E\xF1\xB1\x8C\x5A\x9C\xAC\x2C\x28\x28\x28\x9C\xAC\x30\x18\xA8\
\x98\x81\x28\x34\x3C\x97\x24\xA7\x28\x34\x3C\x9C\x24\xF2\xB0\x89\
\xAC\x91\x2C\x4C\x6C\x8A\x9B\x2D\xD9\xD8\xD8\x51\xD9\xD8\xD8\x79''')

        banks[7] = bytearray(b'''\
\xD9\xD8\xD8\xF1\x9E\x88\xA3\x31\xDA\xD8\xD8\x91\x2D\xD9\x28\xD8\
\x4D\xD9\x48\xD8\x6D\xD9\x68\xD8\xB1\x83\x93\x35\x3D\x80\x25\xDA\
\xD8\xD8\x85\x69\xDA\xD8\xD8\xB4\x93\x81\xA3\x28\x34\x3C\xF3\xAB\
\x8B\xF8\xA3\x91\xB6\x09\xB4\xD9\xAB\xDE\xFA\xB0\x87\x9C\xB9\xA3\
\xDD\xF1\x20\x28\x30\x38\x9A\xF1\x28\x30\x38\x9D\xF1\xA3\xA3\xA3\
\xA3\xF2\xA3\xB4\x90\x80\xF2\xA3\xA3\xA3\xA3\xA3\xA3\xA3\xA3\xA3\
\xA3\xB2\xA3\xA3\xA3\xA3\xA3\xA3\xB0\x87\xB5\x99\xF1\x28\x30\x38\
\x98\xF1\xA3\xA3\xA3\xA3\x97\xA3\xA3\xA3\xA3\xF3\x9B\xA3\x30\xDC\
\xB9\xA7\xF1\x26\x26\x26\xFE\xD8\xFF''')

        dmpMemory = bytearray()
        print("No of banks: {:d}".format(len(banks)))
        for i in range(len(banks)):
            dmpMemory += banks[i]
            
        if self.debug :
            print("Size of dmpMemory: {:d}".format(len(dmpMemory)))
            # for i in range(len(dmpMemory)):
                # if not i == 0 and not i % 16:
                    # print("")
                # if not i % 256:
                    # print("Bank ",i//256) 
                # print("0x{:02x} ".format(dmpMemory[i]),end = "")
                        
            # print("")

        test_data = dmpMemory[:2*MPU6050_DMP_MEMORY_CHUNK_SIZE]
        
        MPU6050_DMP_FIFO_RATE_DIVISOR = 0x01 # The New instance of the Firmware has this as the default

        # reset device
        if self.debug :
            print("Resetting MPU6050 Digital Motion Processor...")
        self.reset()
        sleep_ms(30) # wait after reset

        '''
        # enable sleep mode and wake cycle
        if self.debug:
            print("Enabling sleep mode...")
        self.setSleepEnabled(True)
        if self.debug:
	    print("Enabling wake cycle...")
	self.setWakeCycleEnabled(True)
        '''
        
	# disable sleep mode
	self.setSleepEnabled(False)

	# get MPU hardware revision
	self.setMemoryBank(0x10, True, True)
	self.setMemoryStartAddress(0x06)
	if self.debug:
            print("Checking hardware revision...")
	    print("Revision @ user[16][6] = 0x{:02x}".format(self.readMemoryByte()))

	    print("Resetting memory bank selection to 0...")
            
	self.setMemoryBank(0)
	self.setMemoryStartAddress(0)
        
	# check OTP bank valid
        if self.debug :
	    print("Reading OTP bank valid flag...")
	print("OTP bank is ",end='')
        if self.getOTPBankValid():
            print("valid!")
        else :
            print("invalid")
    
	# setup weird slave stuff (?)
        if self.debug :
	    print("Setting slave 0 address to 0x7F...")
	self.setSlaveAddress(0, 0x7F)
        if self.debug :
	    print("Disabling I2C Master mode...")
	self.setI2CMasterModeEnabled(False)
        if self.debug :
	    print("Setting slave 0 address to 0x68 (self)...")
	self.setSlaveAddress(0, 0x68)
        if self.debug :
	    print("Resetting I2C Master control...")
	self.resetI2CMaster()
	sleep_ms(20)
        if self.debug :
	    print("Setting clock source to Z Gyro...")
	self.setClockSource(MPU6050_CLOCK_PLL_ZGYRO)

	if self.debug :
            print("Setting DMP and FIFO_OFLOW interrupts enabled...")
	self.setIntEnabled(1<<MPU6050_INTERRUPT_FIFO_OFLOW_BIT|1<<MPU6050_INTERRUPT_DMP_INT_BIT)

	if self.debug :
            print("Setting sample rate to 200Hz...")
	self.setRate(4)  # 1khz / (1 + 4) = 200 Hz

	if self.debug :
            print("Setting external frame sync to TEMP_OUT_L[0]...")
	self.setExternalFrameSync(MPU6050_EXT_SYNC_TEMP_OUT_L)

	if self.debug :
            print("Setting DLPF bandwidth to 42Hz...")
	self.setDLPFMode(MPU6050_DLPF_BW_42)

	if self.debug :
            print("Setting gyro sensitivity to +/- 2000 deg/sec...")
	self.setFullScaleGyroRange(MPU6050_GYRO_FS_2000)

	# load DMP code into memory banks
        if self.debug :
	    print("Writing DMP code to MPU memory banks ({:d} bytes)".format(len(dmpMemory)))

	if not self.writeProgMemoryBlock(dmpMemory):
            print("Writing memory block failed")
            return # Failed
	if self.debug :
            print("Success! DMP code written and verified.")
	# load DMP code into memory banks
        if self.debug :
	    print("Writing DMP code to MPU memory banks ({:d} bytes)".format(len(dmpMemory)))

	if not self.writeProgMemoryBlock(dmpMemory):
            print("Writing memory block failed")
            return # Failed
	if self.debug :
            print("Success! DMP code written and verified.")

	# Set the FIFO Rate Divisor int the DMP Firmware Memory
	dmpUpdate = bytearray(2)
        dmpUpdate[0] = 0
        dmpUpdate[1] = MPU6050_DMP_FIFO_RATE_DIVISOR
	self.writeMemoryBlock(dmpUpdate, 0x02, 0x02, 0x16) # Lets write the dmpUpdate data to the Firmware image, 
                                                           # we have 2 bytes to write in bank 0x02 with the Offset 0x16

	# write start address MSB into register
	self.setDMPConfig1(0x03)
	# write start address LSB into register
	self.setDMPConfig2(0x00)

	if self.debug:
            print("Clearing OTP Bank flag...")
	self.setOTPBankValid(False)

	if self.debug:
            print("Setting motion detection threshold to 2...")
	self.setMotionDetectionThreshold(2)

	if self.debug:
            print("Setting zero-motion detection threshold to 156...")
	self.setZeroMotionDetectionThreshold(156)

	if self.debug:
            print("Setting motion detection duration to 80...")
	self.setMotionDetectionDuration(80);

	if self.debug:
            print("Setting zero-motion detection duration to 0...")
	self.setZeroMotionDetectionDuration(0)
	if self.debug:
            print("Enabling FIFO...")
	self.setFIFOEnabled(True)

	if self.debug:
            print("Resetting DMP...")
	self.resetDMP()

        if self.debug:
            print("DMP is good to go! Finally.")

	if self.debug:
            print("Disabling DMP (you turn it on later)...")
	self.setDMPEnabled(False)

        if self.debug:
	    print("Setting up internal 42-byte (default) DMP packet buffer...")
	self.dmpPacketSize = 42

        if self.debug:
            print("Resetting FIFO and clearing INT status one last time...")
	self.resetFIFO();
	self.getIntStatus()

        print("DMP successfully set up")
	return  # success

    # Nothing else changed

    def dmpPacketAvailable():
        return getFIFOCount() >= SELF.dmpGetFIFOPacketSize();
    '''
uint8_t MPU6050_6Axis_MotionApps20::dmpGetAccel(int32_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = (((uint32_t)packet[28] << 24) | ((uint32_t)packet[29] << 16) | ((uint32_t)packet[30] << 8) | packet[31]);
    data[1] = (((uint32_t)packet[32] << 24) | ((uint32_t)packet[33] << 16) | ((uint32_t)packet[34] << 8) | packet[35]);
    data[2] = (((uint32_t)packet[36] << 24) | ((uint32_t)packet[37] << 16) | ((uint32_t)packet[38] << 8) | packet[39]);
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetAccel(int16_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = (packet[28] << 8) | packet[29];
    data[1] = (packet[32] << 8) | packet[33];
    data[2] = (packet[36] << 8) | packet[37];
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetAccel(VectorInt16 *v, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    v -> x = (packet[28] << 8) | packet[29];
    v -> y = (packet[32] << 8) | packet[33];
    v -> z = (packet[36] << 8) | packet[37];
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetQuaternion(int32_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = (((uint32_t)packet[0] << 24) | ((uint32_t)packet[1] << 16) | ((uint32_t)packet[2] << 8) | packet[3]);
    data[1] = (((uint32_t)packet[4] << 24) | ((uint32_t)packet[5] << 16) | ((uint32_t)packet[6] << 8) | packet[7]);
    data[2] = (((uint32_t)packet[8] << 24) | ((uint32_t)packet[9] << 16) | ((uint32_t)packet[10] << 8) | packet[11]);
    data[3] = (((uint32_t)packet[12] << 24) | ((uint32_t)packet[13] << 16) | ((uint32_t)packet[14] << 8) | packet[15]);
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetQuaternion(int16_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = ((packet[0] << 8) | packet[1]);
    data[1] = ((packet[4] << 8) | packet[5]);
    data[2] = ((packet[8] << 8) | packet[9]);
    data[3] = ((packet[12] << 8) | packet[13]);
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetQuaternion(Quaternion *q, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    int16_t qI[4];
    uint8_t status = dmpGetQuaternion(qI, packet);
    if (status == 0) {
        q -> w = (float)qI[0] / 16384.0f;
        q -> x = (float)qI[1] / 16384.0f;
        q -> y = (float)qI[2] / 16384.0f;
        q -> z = (float)qI[3] / 16384.0f;
        return 0;
    }
    return status; // int16 return value, indicates error if this line is reached
}
// uint8_t MPU6050_6Axis_MotionApps20::dmpGet6AxisQuaternion(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetRelativeQuaternion(long *data, const uint8_t* packet);
uint8_t MPU6050_6Axis_MotionApps20::dmpGetGyro(int32_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = (((uint32_t)packet[16] << 24) | ((uint32_t)packet[17] << 16) | ((uint32_t)packet[18] << 8) | packet[19]);
    data[1] = (((uint32_t)packet[20] << 24) | ((uint32_t)packet[21] << 16) | ((uint32_t)packet[22] << 8) | packet[23]);
    data[2] = (((uint32_t)packet[24] << 24) | ((uint32_t)packet[25] << 16) | ((uint32_t)packet[26] << 8) | packet[27]);
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetGyro(int16_t *data, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    data[0] = (packet[16] << 8) | packet[17];
    data[1] = (packet[20] << 8) | packet[21];
    data[2] = (packet[24] << 8) | packet[25];
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpGetGyro(VectorInt16 *v, const uint8_t* packet) {
    // TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == 0) packet = dmpPacketBuffer;
    v -> x = (packet[16] << 8) | packet[17];
    v -> y = (packet[20] << 8) | packet[21];
    v -> z = (packet[24] << 8) | packet[25];
    return 0;
}
// uint8_t MPU6050_6Axis_MotionApps20::dmpSetLinearAccelFilterCoefficient(float coef);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetLinearAccel(long *data, const uint8_t* packet);
uint8_t MPU6050_6Axis_MotionApps20::dmpGetLinearAccel(VectorInt16 *v, VectorInt16 *vRaw, VectorFloat *gravity) {
    // get rid of the gravity component (+1g = +8192 in standard DMP FIFO packet, sensitivity is 2g)
    v -> x = vRaw -> x - gravity -> x*8192;
    v -> y = vRaw -> y - gravity -> y*8192;
    v -> z = vRaw -> z - gravity -> z*8192;
    return 0;
}
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetLinearAccelInWorld(long *data, const uint8_t* packet);
uint8_t MPU6050_6Axis_MotionApps20::dmpGetLinearAccelInWorld(VectorInt16 *v, VectorInt16 *vReal, Quaternion *q) {
    // rotate measured 3D acceleration vector into original state
    // frame of reference based on orientation quaternion
    memcpy(v, vReal, sizeof(VectorInt16));
    v -> rotate(q);
    return 0;
}
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetGyroAndAccelSensor(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetGyroSensor(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetControlData(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetTemperature(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetGravity(long *data, const uint8_t* packet);
uint8_t MPU6050_6Axis_MotionApps20::dmpGetGravity(int16_t *data, const uint8_t* packet) {
    /* +1g corresponds to +8192, sensitivity is 2g. */
    int16_t qI[4];
    uint8_t status = dmpGetQuaternion(qI, packet);
    data[0] = ((int32_t)qI[1] * qI[3] - (int32_t)qI[0] * qI[2]) / 16384;
    data[1] = ((int32_t)qI[0] * qI[1] + (int32_t)qI[2] * qI[3]) / 16384;
    data[2] = ((int32_t)qI[0] * qI[0] - (int32_t)qI[1] * qI[1]
	       - (int32_t)qI[2] * qI[2] + (int32_t)qI[3] * qI[3]) / (int32_t)(2 * 16384L);
    return status;
}

uint8_t MPU6050_6Axis_MotionApps20::dmpGetGravity(VectorFloat *v, Quaternion *q) {
    v -> x = 2 * (q -> x*q -> z - q -> w*q -> y);
    v -> y = 2 * (q -> w*q -> x + q -> y*q -> z);
    v -> z = q -> w*q -> w - q -> x*q -> x - q -> y*q -> y + q -> z*q -> z;
    return 0;
}
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetUnquantizedAccel(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetQuantizedAccel(long *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetExternalSensorData(long *data, int size, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetEIS(long *data, const uint8_t* packet);

uint8_t MPU6050_6Axis_MotionApps20::dmpGetEuler(float *data, Quaternion *q) {
    data[0] = atan2(2*q -> x*q -> y - 2*q -> w*q -> z, 2*q -> w*q -> w + 2*q -> x*q -> x - 1);   // psi
    data[1] = -asin(2*q -> x*q -> z + 2*q -> w*q -> y);                              // theta
    data[2] = atan2(2*q -> y*q -> z - 2*q -> w*q -> x, 2*q -> w*q -> w + 2*q -> z*q -> z - 1);   // phi
    return 0;
}

#ifdef USE_OLD_DMPGETYAWPITCHROLL
uint8_t MPU6050_6Axis_MotionApps20::dmpGetYawPitchRoll(float *data, Quaternion *q, VectorFloat *gravity) {
    // yaw: (about Z axis)
    data[0] = atan2(2*q -> x*q -> y - 2*q -> w*q -> z, 2*q -> w*q -> w + 2*q -> x*q -> x - 1);
    // pitch: (nose up/down, about Y axis)
    data[1] = atan(gravity -> x / sqrt(gravity -> y*gravity -> y + gravity -> z*gravity -> z));
    // roll: (tilt left/right, about X axis)
    data[2] = atan(gravity -> y / sqrt(gravity -> x*gravity -> x + gravity -> z*gravity -> z));
    return 0;
}
#else 
uint8_t MPU6050_6Axis_MotionApps20::dmpGetYawPitchRoll(float *data, Quaternion *q, VectorFloat *gravity) {
    // yaw: (about Z axis)
    data[0] = atan2(2*q -> x*q -> y - 2*q -> w*q -> z, 2*q -> w*q -> w + 2*q -> x*q -> x - 1);
    // pitch: (nose up/down, about Y axis)
    data[1] = atan2(gravity -> x , sqrt(gravity -> y*gravity -> y + gravity -> z*gravity -> z));
    // roll: (tilt left/right, about X axis)
    data[2] = atan2(gravity -> y , gravity -> z);
    if (gravity -> z < 0) {
        if(data[1] > 0) {
            data[1] = PI - data[1]; 
        } else { 
            data[1] = -PI - data[1];
        }
    }
    return 0;
}
#endif

// uint8_t MPU6050_6Axis_MotionApps20::dmpGetAccelFloat(float *data, const uint8_t* packet);
// uint8_t MPU6050_6Axis_MotionApps20::dmpGetQuaternionFloat(float *data, const uint8_t* packet);

uint8_t MPU6050_6Axis_MotionApps20::dmpProcessFIFOPacket(const unsigned char *dmpData) {
    (void)dmpData; // unused parameter
    /*for (uint8_t k = 0; k < dmpPacketSize; k++) {
        if (dmpData[k] < 0x10) Serial.print("0");
        Serial.print(dmpData[k], HEX);
        Serial.print(" ");
    }
    Serial.print("\n");*/
    //Serial.println((uint16_t)dmpPacketBuffer);
    return 0;
}
uint8_t MPU6050_6Axis_MotionApps20::dmpReadAndProcessFIFOPacket(uint8_t numPackets, uint8_t *processed) {
    uint8_t status;
    uint8_t buf[dmpPacketSize];
    for (uint8_t i = 0; i < numPackets; i++) {
        // read packet from FIFO
        getFIFOBytes(buf, dmpPacketSize);

        // process packet
        if ((status = dmpProcessFIFOPacket(buf)) > 0) return status;
        
        // increment external process count variable, if supplied
        if (processed != 0) (*processed)++;
    }
    return 0;
}

// uint8_t MPU6050_6Axis_MotionApps20::dmpSetFIFOProcessedCallback(void (*func) (void));

// uint8_t MPU6050_6Axis_MotionApps20::dmpInitFIFOParam();
// uint8_t MPU6050_6Axis_MotionApps20::dmpCloseFIFO();
// uint8_t MPU6050_6Axis_MotionApps20::dmpSetGyroDataSource(uint_fast8_t source);
// uint8_t MPU6050_6Axis_MotionApps20::dmpDecodeQuantizedAccel();
// uint32_t MPU6050_6Axis_MotionApps20::dmpGetGyroSumOfSquare();
// uint32_t MPU6050_6Axis_MotionApps20::dmpGetAccelSumOfSquare();
// void MPU6050_6Axis_MotionApps20::dmpOverrideQuaternion(long *q);
uint16_t MPU6050_6Axis_MotionApps20::dmpGetFIFOPacketSize() {
    return dmpPacketSize;
}



uint8_t MPU6050_6Axis_MotionApps20::dmpGetCurrentFIFOPacket(uint8_t *data) { // overflow proof
    return(GetCurrentFIFOPacket(data, dmpPacketSize));
}
'''
m6050_dmp = MPU6050_DMP(debug=True)
