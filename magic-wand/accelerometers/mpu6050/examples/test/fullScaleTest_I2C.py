from machine import Pin,I2C
from utime import sleep_ms

MPU6050_ADDRESS = 0x68

MPU6050_ACCEL_CONFIG = 0x1c
MPU6050_WHO_AM_I     = 0x75
MPU6050_FIFO         = 0x74
MPU6050_INT_ENABLE   = 0x38   
MPU6050_PWR_MGMT_1   = 0x6b
MPU6050_MPT_THR      = 0x1f
i2c = I2C(1,scl=Pin(22),sda=Pin(21))

print("Reset the chip")
tmp = bytes(b'\x80')
i2c.writeto_mem(MPU6050_ADDRESS,MPU6050_PWR_MGMT_1,tmp)
sleep_ms(50) # sleep 50 ms to let the chip come up

tmp = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_WHO_AM_I,1)[0] >> 1
print("DeviceID: 0x{:02x}".format(tmp))

print("Write to FIFO")
tmp = bytes(b'\x55\xaa')
print("byte array: {} in hex: 0x{:02x},0x{:02x}".format(tmp,tmp[0],tmp[1]))
i2c.writeto_mem(MPU6050_ADDRESS,MPU6050_FIFO,tmp)

readback = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_FIFO,2)
print("Read from FIFO: 0x{:02x},0x{:02x}".format(readback[0],readback[1]))

readback = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_INT_ENABLE,1)[0]
print("Interrupt enable register: 0x{:02x}".format(readback))

print("write 0x41 to the interrupt enable register")
tmp = bytes(b'\x41')
i2c.writeto_mem(MPU6050_ADDRESS,MPU6050_INT_ENABLE,tmp)

readback = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_INT_ENABLE,1)[0]
print("Interrupt enable register: 0x{:02x}\n".format(readback))

print("Set the digital high pass filter and accelerometer full scale")
tmp = bytes(b'\x13')
i2c.writeto_mem(MPU6050_ADDRESS,MPU6050_ACCEL_CONFIG,tmp)
readback = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_ACCEL_CONFIG,1)[0]
print("Accelerometer config: 0x{:02x}\n".format(readback))

print("write 0xaa to motion detection threshold register")
tmp = bytes(b'\xaa')
i2c.writeto_mem(MPU6050_ADDRESS,MPU6050_MPT_THR,tmp)

readback = i2c.readfrom_mem(MPU6050_ADDRESS,MPU6050_MPT_THR,1)[0]
print("Motion detection threshold register: 0x{:02x}\n".format(readback))
