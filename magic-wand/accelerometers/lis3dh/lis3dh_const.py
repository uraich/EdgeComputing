# lis3dh_const.py: constants used be the lis3dh accelerometer driver
# Copyright (c) U. Raich, March 2022
# This program is part of the course on TinyML at the University of Cape Coast, Ghana
# It is released under the MIT license

from micropython import const
LIS3DH_READ                     = const(0x80)
LIS3DH_WRITE                    = const(0x00)
LIS3DH_ADDR_UNCHANGED           = const(0x00)
LIS3DH_ADDR_CHANGES             = const(0x40)
LIS3DH_ID                       = const(0x33)
LIS3DH_I2C_ADDR                 = const(0x18)

LIS3DH_STATUS_REG_AUX           = const(0x07)
LIS3DH_OUT_ADC1_L               = const(0x08)
LIS3DH_OUT_ADC1_H               = const(0x09)
LIS3DH_OUT_ADC2_L               = const(0x0a)
LIS3DH_OUT_ADC2_H               = const(0x0b)
LIS3DH_OUT_ADC3_L               = const(0x0c)
LIS3DH_OUT_ADC3_H               = const(0x0d)
LIS3DH_WHO_AM_I                 = const(0x0f)
LIS3DH_CTRL_REG0                = const(0x1e)
LIS3DH_TEMP_CFG_REG             = const(0x1f)
LIS3DH_CTRL_REG1                = const(0x20)
LIS3DH_CTRL_REG2                = const(0x21)
LIS3DH_CTRL_REG3                = const(0x22)
LIS3DH_CTRL_REG4                = const(0x23)
LIS3DH_CTRL_REG5                = const(0x24)
LIS3DH_CTRL_REG6                = const(0x25)
LIS3DH_REFERENCE                = const(0x26)
LIS3DH_STATUS_REG               = const(0x27)
LIS3DH_OUT_X_L                  = const(0x28)
LIS3DH_OUT_X_H                  = const(0x29)
LIS3DH_OUT_Y_L                  = const(0x2a)
LIS3DH_OUT_Y_H                  = const(0x2b)
LIS3DH_OUT_Z_L                  = const(0x2c)
LIS3DH_OUT_Z_H                  = const(0x2d)
LIS3DH_FIFO_CTRL_REG            = const(0x2e)
LIS3DH_FIFO_SRC_REG             = const(0x2f)
LIS3DH_INT1_CFG                 = const(0x30)
LIS3DH_INT1_SRC                 = const(0x31)
LIS3DH_INT1_THS                 = const(0x32)
LIS3DH_INT1_DURATION            = const(0x33)
LIS3DH_INT2_CFG                 = const(0x34)
LIS3DH_INT2_SRC                 = const(0x35)
LIS3DH_INT2_THS                 = const(0x36)
LIS3DH_INT2_DURATION            = const(0x37)
LIS3DH_CLICK_CFG                = const(0x38)
LIS3DH_CLICK_SRC                = const(0x39)
LIS3DH_CLICK_THS                = const(0x3a)
LIS3DH_TIME_LIMIT               = const(0x3b)
LIS3DH_TIME_LATENCY             = const(0x3c)
LIS3DH_TIME_WINDOW              = const(0x3d)
LIS3DH_ACT_THS                  = const(0x3e)
LIS3DH_ACT_DUR                  = const(0x3f)

# Status register aux
DATA_AVAILABLE_1                = 0 # data available
DATA_AVAILABLE_2                = 1
DATA_AVAILABLE_3                = 2
DATA_AVAILABLE_321              = 3
OVERRUN_1                       = 4 # overrun error
OVERRUN_2                       = 5
OVERRUN_3                       = 6
OVERRUN_321                     = 7

# Status register
DATA_AVAILABLE_X                = 0 # data available
DATA_AVAILABLE_Y                = 1
DATA_AVAILABLE_Z                = 2
DATA_AVAILABLE_XYZ              = 3
OVERRUN_X                       = 4 # overrun error
OVERRUN_Y                       = 5
OVERRUN_Z                       = 6
OVERRUN_XYZ                     = 7

# CTRL_REG0
SD0_PU_DISC                     = 7

# TEMP_CFG_REG
ADC_PD                          = 7
TEMP_EN                         = 6

# CTRL_REG1
RATE_POS                        = 7
RATE_SIZE                       = 4

LP_EN                           = 3
Z_EN                            = 2
Y_EN                            = 1
X_EN                            = 0

ALL_AXIS_EN_POS                 = 2
ALL_AXIS_EN_SIZE                = 3

RATE_POWER_DOWN                 = 0
RATE_1HZ                        = 1
RATE_10HZ                       = 2
RATE_25HZ                       = 3
RATE_50HZ                       = 4
RATE_100HZ                      = 5
RATE_200HZ                      = 6
RATE_400HZ                      = 7
RATE_1600HZ                     = 8
RATE_1344HZ                     = 9

#CTRL_REG2

HP_FILTER_MODE_POS              = 7
HP_FILTER_MODE_SIZE             = 2

HP_FILTER_CUTOFF_POS            = 5
HP_FILTER_CUTOFF_SIZE           = 2

FILTER_DATA_SEL                 = 3
HP_CLICK                        = 2
HP_IA2                          = 1
HP_IA1                          = 0

HP_MODE_NORMAL_RES              = 0
REF_SIGNAL                      = 1
HP_MODE_NORMAL                  = 2
AUTO_RESET                      = 3

# CTRL_REG3

I1_CLICK                        = 7
I1_IA1                          = 6
I1_IA2                          = 5
I1_ZYXDA                        = 4
I1_321DA                        = 3
I1_WTM                          = 2
I1_OVERRUN                      = 1

# CTRL_REG4

BDU                             = 7
BLE                             = 6
FULL_SCALE_POS                  = 5
FULL_SCALE_SIZE                 = 2
HIGH_RES                        = 3
SELF_TEST_POS                   = 2
SELF_TEST_SIZE                  = 2
SERIAL_INTERFACE_MODE           = 0

# CTRL_REG5

BOOT                            = 7
FIFO_EN                         = 6
LIR_INT1                        = 3
D4D_INT1                        = 2
LIR_INT2                        = 1
D4D_INT2                        = 0

# CTRL_REG6

I2_CLICK                        = 7
I2_IA1                          = 6
I2_IA2                          = 5
I2_BOOT                         = 4
I2_ACT                          = 3
INT_POLARITY                    = 1

# STATUS_REG

ZYX_OVERRUN                     = 7
Z_OVERRUN                       = 6
Y_OVERRUN                       = 5
X_OVERRUN                       = 4
ZYX_DATA_AVAILABLE              = 3
Z_DATA_AVAILABLE                = 2
Y_DATA_AVAILABLE                = 1
X_DATA_AVAILABLE                = 0

# FIFO_CTRL_REG

FIFO_MODE_POS                   = 7
FIFO_MODE_SIZE                  = 2

FIFO_BYPASS                     = 0
FIFO_MODE_FIFO                  = 1
FIFO_MODE_STREAM                = 2
FIFO_MODE_STREAM_TO_FIFO        = 3

TRIGGER_SELECT                  = 5

FIFO_THRESHOLD_POS              = 4
FIFO_THRESHOLD_SIZE             = 5

#FIFO_SRC_REG

FIFO_WATERMARK                  = 7
FIFO_OVERRUN                    = 6
FIFO_EMPTY                      = 5

FIFO_NO_OF_SAMPLES_POS          = 4
FIFO_NO_OF_SAMPLES_SIZE         = 5

# INT1_CFG

INT1_AOI                        = 7
INT1_6D                         = 6
INT1_ZHIE                       = 5
INT1_ZLIE                       = 4
INT1_YHIE                       = 3
INT1_YLIE                       = 2
INT1_XHIE                       = 1
INT1_XLIE                       = 0

INT_MODE_POS                    = 7
INT_MODE_SIZE                   = 2

# INT1_SRC

INT1_SRC_IA                     = 6
INT1_SRC_ZH                     = 5
INT1_SRC_ZL                     = 4
INT1_SRC_YH                     = 3
INT1_SRC_YL                     = 2
INT1_SRC_ZH                     = 1
INT1_SRC_ZL                     = 0

# INT2_CFG
INT2_AOI                        = 7
INT2_6D                         = 6
INT2_ZHIE                       = 5
INT2_ZLIE                       = 4
INT2_YHIE                       = 3
INT2_YLIE                       = 2
INT2_XHIE                       = 1
INT2_XLIE                       = 0

# INT2_SRC

INT2_SRC_IA                     = 6
INT2_SRC_ZH                     = 5
INT2_SRC_ZL                     = 4
INT2_SRC_YH                     = 3
INT2_SRC_YL                     = 2
INT2_SRC_ZH                     = 1
INT2_SRC_ZL                     = 0

# CLICK_CFG

CLICK_ZD                        = 5
CLICK_ZS                        = 4
CLICK_YD                        = 3
CLICK_YS                        = 2
CLICK_XD                        = 1
CLICK_XS                        = 0

# CLICK_SRC

CLICK_SRC_IA                    = 6
CLICK_SRC_DCLICK                = 5
CLICK_SRC_SCLICK                = 4
CLICK_SRC_SIGN                  = 3
CLICK_SRC_Z                     = 2
CLICK_SRC_Y                     = 1
CLICK_SRC_Y                     = 0

# CLICK_THS
LIR_CLICK                       = 7
CLICK_THRESHOLD_POS             = 6
CLICK_THRESHOLD_SIZE            = 7

