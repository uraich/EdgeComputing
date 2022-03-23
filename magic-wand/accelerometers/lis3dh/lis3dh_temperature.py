from lis3dh_i2c import LIS3DH_I2C
from lis3dh_const import *
from utime import sleep_ms

# Create a LIS3DH onject running on the I2C bus
lis3dh_i2c = LIS3DH_I2C()
print("Enable debugging information")
lis3dh_i2c.degugging = False

print("Reboot the device")
lis3dh_i2c.boot = True
sleep_ms(5)
print("CTRL_REG_5 after boot: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5 ))

# set the data rate to 25 Hz
print("Set data rate to 25 Hz")
lis3dh_i2c.data_rate = RATE_25HZ

#  enable all axes, normal mode
lis3dh_i2c.all_axis_enable =True

# set the BDU bit in CTRL_REG 4, see section 3.7 of the data sheet
print("Set the Block Data Update (BDU) bit in CTRL_REG4. Needed to access the ADCs and the temperature sensor")
lis3dh_i2c.block_data_update = True

# enable high resolution
print("Set to high resolution")
lis3dh_i2c.high_res = True

# enable the ADCs
print("Enable the ADCs")
lis3dh_i2c.adc_enable = True

# enable the Temperature sensor
print("Enable the temperature sensor")
lis3dh_i2c.temp_enable = True

print("CTRL_REG1: 0x{:02x}".format(lis3dh_i2c.ctrl_reg1))
print("CTRL_REG2: 0x{:02x}".format(lis3dh_i2c.ctrl_reg2))
print("CTRL_REG4: 0x{:02x}".format(lis3dh_i2c.ctrl_reg4))
print("CTRL_REG5: 0x{:02x}".format(lis3dh_i2c.ctrl_reg5))
print("Data rate: ",lis3dh_i2c.print_rate(lis3dh_i2c.data_rate))

while True:
    # lis3dh_i2c.debugging = True
    temperature = lis3dh_i2c.temperature
    print("temperature: {:d}°C".format(temperature))
    sleep_ms(100)

