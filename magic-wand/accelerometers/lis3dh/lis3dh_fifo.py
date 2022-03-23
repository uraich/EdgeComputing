from lis3dh_i2c import LIS3DH_I2C
from lis3dh_const import *
from utime import sleep_ms

# Create a LIS3DH onject running on the I2C bus
lis3dh_i2c = LIS3DH_I2C()
print("Enable debugging information")
lis3dh_i2c.debugging = False

print("Reboot the device")
lis3dh_i2c.boot = True
sleep_ms(5)
# ctrl5 = lis3dh_i2c.ctrl_reg5
print("CTRL_REG_5 after boot: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5))

# set the data rate to 100 Hz
print("Set data rate to 100 Hz")
lis3dh_i2c.data_rate = RATE_100HZ

# enable high resolution
print("Set to high resolution")
lis3dh_i2c.high_res = True

# set FIFO to FIFO mode
print("Seting FIFO to FIFO mode")
lis3dh_i2c.fifo_mode = FIFO_MODE_FIFO
print("FIFO mode is now " + lis3dh_i2c.print_fifo_mode(lis3dh_i2c.fifo_mode))
#enable the FIFO
lis3dh_i2c.fifo_enable = True

print("CTRL_REG1: 0x{:02x}".format(lis3dh_i2c.ctrl_reg1))

print("CTRL_REG2: 0x{:02x}".format(lis3dh_i2c.ctrl_reg2))
print("CTRL_REG4: 0x{:02x}".format(lis3dh_i2c.ctrl_reg4))
print("CTRL_REG5: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5))
print("Data rate: ",lis3dh_i2c.print_rate(lis3dh_i2c.data_rate))
print("FIFO control register: 0x{:02x}".format(lis3dh_i2c.fifo_ctrl_reg))

print("Fifo no of samples: {:d}".format(lis3dh_i2c.fifo_no_of_samples))
lis3dh_i2c.clear_fifo()
print("status_reg: 0x{:02x}".format(lis3dh_i2c.status))

#  enable all axes, normal mode
lis3dh_i2c.all_axis_enable = True

while True:
    if not lis3dh_i2c.fifo_empty :
        if lis3dh_i2c.zyx_overrun :
            print("Overrun error")
            lis3dh_i2c.clear_fifo()    
        else:
            accel=lis3dh_i2c.accel_raw
            print("accel_x: {:d}, accel_y: {:d}, accel_z: {:d}".format(accel[0],accel[1],accel[2]))
    else :
        sleep_ms(1)
