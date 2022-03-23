from lis3dh_const import *
from machine import SPI,SoftSPI,Pin,Signal
import sys
import ustruct as struct
from utime import sleep_ms

class LIS3DH:
    def __init__(self,sck=18,mosi=23,miso=19,cs=26,debug=False) :
        self.debug = debug
        self.bus = None
        self.temperature_calib = 37 # read 0xf4 = -13 when at 24°C. Therefore the offset is 37

    @property
    def debugging(self) :
        self.debug = onOff
    @debugging.setter
    def debugging(self,onOff) :
        self.debug = onOff
        
    def read_byte(self, reg_addr) :     # dummy read_byte, must be overridden by sub class
        raise Exception("read_byte must be implemented by the sub class")

    def write_byte(self, reg_addr, value) :     # dummy read_byte, must be overridden by sub class
        print("write_byte must be implemented by the sub class")

    def read_bytes(self,reg_addr,no_of_bytes) :
        print("read_bytes must be implemented by the sub class")

    def read_word(self, reg_addr) : # dummy read_byte, must be overridden by sub class
        raise Exception("read_word must be implemented by the sub class")

    def get_bit(self,reg_addr,bit_no) :
        mask = 1 << bit_no
        return (self.read_byte(reg_addr) & mask) >> bit_no
    
    def set_bit(self,reg_addr,bit_no,on_off) :
        mask = 1 << bit_no
        current_value = self.read_byte(reg_addr)
        if self.debug :
            print("Current value in register 0x{:02x}: 0x{:02x}".format(reg_addr,current_value))
        if on_off :
            new_value = current_value | mask
        else :
            new_value = current_value & ~mask
        if self.debug :
            print("New value in register 0x{:02x}: 0x{:02x}".format(reg_addr,new_value))            
        self.write_byte(reg_addr,new_value)

    def set_bits(self,reg_addr,bitfield_pos,bitfield_size,value) :
        shift = bitfield_pos - bitfield_size +1
        if self.debug :
            print("Debug: shift = ",shift)
        mask = 1
        for i in range(bitfield_size-1):
            mask <<= 1
            mask |= 1
        mask <<= shift
        if self.debug :
            print("Debug: mask: {:02x}".format(mask))
        mask = ~ mask
        current_value = self.read_byte(reg_addr)
        new_value = current_value & mask
        new_value |= (value << shift)
        if self.debug:
            print("Debug: old value: 0x{:02x}, new value: 0x{:02x}".format(
                current_value,new_value))
        self.write_byte(reg_addr,new_value)
            
    def get_bits(self,reg_addr,bitfield_pos,bitfield_size) :
        mask = 1
        for _ in range(bitfield_size-1):
            mask <<= 1
            mask |= 1
        shift = bitfield_pos - bitfield_size + 1
        mask <<= shift
        value = (self.read_byte(reg_addr) & mask) >> shift
        if self.debug:
            print("Debug: bitfield value: 0x{:02x}".format(value))
        return value
    
    # STATUS_REG_AUX
    @property
    def status_aux(self) :
        return self.read_byte(LIS3DH_STATUS_REG_AUX)
    @property
    def overrun_321(self):
        return self.get_bit(LIS3DH_STATUS_REG_AUX, OVERRUN_123)    
    @property
    def overrun_3(self):
        return self.get_bit(LIS3DH_STATUS_REG_AUX, OVERRUN_3)    
    @property
    def overrun_2(self):
        return self.get_bit(LIS3DH_STATUS_REG, OVERRUN_2)    
    @property
    def overrun_1(self):
        return self.get_bit(LIS3DH_STATUS_REG, OVERRUN_1)    
    @property
    def data_available_321(self):
        return self.get_bit(LIS3DH_STATUS_REG, DATA_AVAILABLE_321)    
    @property
    def data_available_3(self):
        return self.get_bit(LIS3DH_STATUS_REG, DATA_AVAILABLE_3)    
    @property
    def data_available_2(self):
        return self.get_bit(LIS3DH_STATUS_REG, DATA_AVAILABLE_2)    
    @property
    def data_available_1(self):
        return self.get_bit(LIS3DH_STATUS_REG, DATA_AVAILABLE_1)


    # WHO_AM_I register
    
    def getID(self) :
        return self.read_byte(LIS3DH_WHO_AM_I)

    # CTRL_REG0

    @property
    def ctrl0(self) :
        return self.read_byte(LIS3DH_CTRL_REG0)
    @ctrl0.setter
    def ctrl0(self,value) :
        self.write_byte(LIS3DH_CTRL_REG0,value)
    @property
    def SD0_pullup(self) :
        return self.get_bit(LIS3DH_CTRL_REG0,SD0_PU_DISC)
    @SD0_pullup.setter
    def SD0_pullup(self,value) :
        self.set_bit(LIS3DH_CTRL_REG0,SD0_PU_DISC,value)

    # TEMP_CFG_REG

    @property
    def temp_cfg(self) :
        return self.read_byte(LIS3DH_TEMP_CFG_REG)
    @temp_cfg.setter
    def temp_cfg(self, value) :
        self.write_byte(LIS3DH_TEMP_CFG_REG,value)
    @property
    def adc_enable(self,value) :
        self.get_bit(LIS3DH_TEMP_CFG_REG,ADC_PD)
    @adc_enable.setter
    def adc_enable(self,value) :
        self.set_bit(LIS3DH_TEMP_CFG_REG,ADC_PD,value)
    @property
    def temp_enable(self) :
        self.get_bit(LIS3DH_TEMP_CFG_REG,TEMP_EN)
    @temp_enable.setter
    def temp_enable(self,value) :
        self.set_bit(LIS3DH_TEMP_CFG_REG,TEMP_EN,value)

    # CTRL_REG1
    @property
    def ctrl_reg1(self) :
        return self.read_byte(LIS3DH_CTRL_REG1)
    @ctrl_reg1.setter
    def ctrl_reg1(self, value) :
        self.write_byte(LIS3DH_CTRL_REG1,value)

    @property
    def data_rate(self) :
        return self.get_bits(LIS3DH_CTRL_REG1,RATE_POS,RATE_SIZE)

    @data_rate.setter
    def data_rate(self,rate) :
        self.set_bits(LIS3DH_CTRL_REG1,RATE_POS,RATE_SIZE,rate)

    def print_rate(self,rate) :
        rate_signification = {RATE_POWER_DOWN: "power down",
                             RATE_1HZ:        "1 Hz",
                             RATE_10HZ:       "10 Hz",
                             RATE_25HZ:       "25 Hz",
                             RATE_50HZ:       "50 Hz",
                             RATE_100HZ:      "100 Hz",
                             RATE_200HZ:      "200 Hz",
                             RATE_400HZ:      "400 Hz",
                             RATE_1600HZ:     "1.6 kHz",
                             RATE_1344HZ:     "1.344 kHz"}
        if self.debug:
            print("Debug: Data rate: ",rate_signification[rate])
            
        return rate_signification[rate]
    @property
    def low_power_enable(self) :
        return self.get_bit(LIS3DH_CTRL_REG1,LP_EN)
    @low_power_enable.setter
    def low_power_enable(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG1,LP_EN,value)
    @property
    def X_enable(self) :
        return self.get_bit(LIS3DH_CTRL_REG1,X_EN)
    @X_enable.setter
    def X_enable(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG1,X_EN,value)
    @property
    def Y_enable(self) :
        return self.get_bit(LIS3DH_CTRL_REG1,Y_EN)
    @Y_enable.setter
    def Y_enable(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG1,Y_EN,value)
    @property
    def Z_enable(self) :
        return self.get_bit(LIS3DH_CTRL_REG1,Z_EN)
    @Y_enable.setter
    def Z_enable(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG1,Z_EN,value)
    @property
    def all_axis_enable(self) :       
        en = self.get_bits(LIS3DH_CTRL_REG1, ALL_AXIS_EN_POS, ALL_AXIS_EN_SIZE)[0]
        if en == 1 << X_EN | 1 << Y_EN | 1 << Z_EN :
            return True
        else:
            return False
    @all_axis_enable.setter
    def all_axis_enable(self,value) :
        if value:
            en = 1 << X_EN | 1 << Y_EN | 1 << Z_EN
        else :
            en = 0
        return self.set_bits(LIS3DH_CTRL_REG1, ALL_AXIS_EN_POS, ALL_AXIS_EN_SIZE,en)


    # CTRL_REG2
    @property
    def ctrl_reg2(self) :
        return self.read_byte(LIS3DH_CTRL_REG2)
    @ctrl_reg2.setter
    def ctrl_reg2(self, value) :
        self.write_byte(LIS3DH_CTRL_REG2,value)
    @property
    def high_pass_mode(self) :
        return self.get_bits(LIS3DH_CTRL_REG2, HP_FILTER_MODE_POS, HP_FILTER_MODE_SIZE)
    @high_pass_mode.setter
    def high_pass_mode(self,value) :
        self.set_bits(LIS3DH_CTRL_REG2, HP_FILTER_MODE_POS, HP_FILTER_MODE_SIZE,value)
    @property
    def high_pass_cutoff(self) :
        return self.get_bits(LIS3DH_CTRL_REG2, HP_FILTER_CUTOFF_POS, HP_FILTER_CUTOFF_SIZE)
    @high_pass_cutoff.setter
    def high_pass_cutoff(self,value) :
        self.set_bits(LIS3DH_CTRL_REG2, HP_FILTER_CUTOFF_POS, HP_FILTER_CUTOFF_SIZE,value)
    @property
    def filtered_selection(self) :
        return self.get_bit(LIS3DH_CTRL_REG2,FILTER_DATA_SEl)
    @filtered_selection.setter
    def filtered_selection(self,value) :
        return self.get_bit(LIS3DH_CTRL_REG2,FILTER_DATA_SEL,value)
        
    # CTRL_REG 3
    @property
    def ctrl_reg3(self) :
        return self.read_byte(LIS3DH_CTRL_REG3)
    @ctrl_reg3.setter
    def ctrl_reg3(self, value) :
        self.write_byte(LIS3DH_CTRL_REG3,value)
    @property
    def i1_click(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_CLICK)
    @i1_click.setter
    def i1_click(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_CLICK, value)
    @property
    def i1_ia1(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_IA1)
    @i1_ia1.setter
    def i1_ia1(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_IA1, value)
    @property
    def i1_ia2(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_IA2)
    @i1_ia2.setter
    def i1_ia2(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_IA2, value)
    @property
    def i1_zyxda(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_ZYXDA)
    @i1_zyxda.setter
    def i1_zyxda(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_ZYXDA, value)
    @property
    def i1_321da(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_321DA)
    @i1_321da.setter
    def i1_321da(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_321DA, value)
    @property
    def i1_wtm(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_WTM)
    @i1_wtm.setter
    def i1_wtm(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_WTM, value)
    @property
    def i1_overrun(self) :
        return self.get_bit(LIS3DH_CTRL_REG3, I1_OVERRUN)
    @i1_overrun.setter
    def i1_overrun(self,value) :
        self.set_bit(LIS3DH_CTRL_REG3, I1_OVERRUN, value)

   
    # CTRL_REG4
    @property
    def ctrl_reg4(self) :
        return self.read_byte(LIS3DH_CTRL_REG4)
    @ctrl_reg4.setter
    def ctrl_reg4(self, value) :
        self.write_byte(LIS3DH_CTRL_REG4,value)
    @property
    def block_data_update(self) :
        return self.get_bit(LIS3DH_CTRL_REG4, BDU)
    @block_data_update.setter
    def block_data_update(self,value) :
        self.set_bit(LIS3DH_CTRL_REG4, BDU, value)
    @property
    def big_endian(self):
        return not self.get_bit(LIS3DH_CTRL_REG4, BLE)
    @big_endian.setter
    def big_endian(self):
        current_value = self.get_ctrl_reg4()
        self.set_ctrl_reg4(current_value & 0xfe)
    @property
    def little_endian(self):
        return self.get_bit(LIS3DH_CTRL_REG4, BLE)
    @little_endian.setter
    def little_endian(self):
        current_value = self.get_ctrl_reg4()
        self.set_ctrl_reg4(current_value | 1)
    @property
    def high_res(self) :
        return self.get_bit(LIS3DH_CTRL_REG4, HIGH_RES)
    @high_res.setter
    def high_res(self,value) :
        self.set_bit(LIS3DH_CTRL_REG4, HIGH_RES, value)
    @property
    def full_scale(self) :
        return self.get_bits(LIS3DH_CTRL_REG4, FULL_SCALE_POS, FULL_SCALE_SIZE)    
    @full_scale.setter
    def full_scale(self,value) :
        return self.set_bits(LIS3DH_CTRL_REG4, FULL_SCALE_POS, FULL_SCALE_SIZE,value)
    @property
    def self_test_enable(self) :
        return self.get_bits(LIS3DH_CTRL_REG4, SELF_TEST_POS, SELF_TEST_SIZE)    
    @self_test_enable.setter
    def self_test_enable(self,value) :
        return self.set_bits(LIS3DH_CTRL_REG4, SELF_TEST_POS, SELF_TEST_SIZE,value)    
    @property
    def spi_mode_3_wire(self) :
        return self.get_bit(LIS3DH_CTRL_REG4, SERIAL_INTERFACE_MODE)
    @spi_mode_3_wire.setter
    def spi_mode_3_wire(self,value) :
        self.set_bit(LIS3DH_CTRL_REG4, SERIAL_INTERFACE_MODE, value)

    # CTRL_REG5
    @property
    def ctrl_reg5(self) :
        return self.read_byte(LIS3DH_CTRL_REG5)
    @ctrl_reg5.setter
    def ctrl_reg5(self, value) :
        self.write_byte(LIS3DH_CTRL_REG5,value)
    @property
    def boot(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, BOOT)    
    @boot.setter
    def boot(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, BOOT, value)    
    @property
    def fifo_enable(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, FIFO_EN)    
    @fifo_enable.setter
    def fifo_enable(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, FIFO_EN, value)    
    @property
    def lir_int1(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, LIR_INT1)    
    @lir_int1.setter
    def lir_int1(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, LIR_INT1, value)    
    @property
    def d4d_int1(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, D4D_INT1)    
    @d4d_int1.setter
    def d4d_int1(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, D4D_INT1, value)    
    @property
    def lir_int2(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, LIR_INT2)    
    @lir_int2.setter
    def lir_int2(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, LIR_INT2, value)    
    @property
    def d4d_int2(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, D4D_INT2)    
    @d4d_int2.setter
    def d4d_int2(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, D4D_INT2, value)

    # CTRL_REG6
    @property
    def ctrl_reg6(self) :
        return self.read_byte(LIS3DH_CTRL_REG6)
    @ctrl_reg6.setter
    def ctrl_reg6(self, value) :
        self.write_byte(LIS3DH_CTRL_REG6,value)
    @property
    def i2_click(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, I2_CLICK)    
    @i2_click.setter
    def i2_click(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, I2CLICK, value)    
    @property
    def i2_ia1(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, I2_IA1)    
    @i2_ia1.setter
    def i2_ia1(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, I2_IA1, value)    
    @property
    def i2_ia2(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, I2_IA2)    
    @i2_ia2.setter
    def i2_ia2(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, I2_IA2, value)    
    @property
    def i2_boot(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, I2_BOOT)    
    @i2_boot.setter
    def i2_boot(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, I2_BOOT, value)    
    @property
    def i2_act(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, I2_ACT)    
    @i2_act.setter
    def i2_act(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, I2_ACT, value)    
    @property
    def int_polarity(self) :
        return self.get_bit(LIS3DH_CTRL_REG5, INT_POLARITY)    
    @int_polarity.setter
    def int_polarity(self,value) :
        return self.set_bit(LIS3DH_CTRL_REG5, INT_POLARITY, value)    

    # REFERENCE
    @property
    def reference(self) :
        return self.read_byte(LIS3DH_CTRL_REFERENCE)
    @reference.setter
    def reference(self, value) :
        self.write_byte(LIS3DH_CTRL_REFERENCE,value)

    # STATUS_REG
    @property
    def status(self) :
        return self.read_byte(LIS3DH_STATUS_REG)
    @property
    def zyx_overrun(self):
        return self.get_bit(LIS3DH_STATUS_REG, ZYX_OVERRUN)    
    @property
    def z_overrun(self):
        return self.get_bit(LIS3DH_STATUS_REG, Z_OVERRUN)    
    @property
    def y_overrun(self):
        return self.get_bit(LIS3DH_STATUS_REG, Y_OVERRUN)    
    @property
    def x_overrun(self):
        return self.get_bit(LIS3DH_STATUS_REG, X_OVERRUN)    
    @property
    def zyx_data_available(self):
        return self.get_bit(LIS3DH_STATUS_REG, ZYX_DATA_AVAILABLE)    
    @property
    def z_data_available(self):
        return self.get_bit(LIS3DH_STATUS_REG, Z_DATA_AVAILABLE)    
    @property
    def y_data_available(self):
        return self.get_bit(LIS3DH_STATUS_REG, Y_DATA_AVAILABLE)    
    @property
    def x_data_available(self):
        return self.get_bit(LIS3DH_STATUS_REG, X_DATA_AVAILABLE)

    # OUT_X_L, OUT_X_H, OUT_Y_L, OUT_Y_H, OUT_Z_L, OUT_Z_H
    @property
    def accel_raw(self) :
        tmp = self.read_bytes(LIS3DH_OUT_X_L | 0x80 ,6)
        if self.debug:
            print("xlow: 0x{:02x}, xhigh: 0x{:02x}, ylow: 0x{:02x}, yhigh: 0x{:02x}, zLow: 0x{:02x}, zhigh: 0x{:02x}".format(
                tmp[0],tmp[1],tmp[2],tmp[3],tmp[4],tmp[5]))
        return struct.unpack('<hhh',tmp)
    @property    
    def accel_X_raw(self) :
        return self.read_word(LIS3DH_OUT_X_L)
    @property
    def accel_Y_raw(self) :
        return self.read_word(LIS3DH_OUT_Y_L)
    @property
    def accel_Z_raw(self) :
        return self.read_word(LIS3DH_OUT_Z_L)

    @property
    def accel(self) :
        full_scale_table = {0:16384, # +- 2g 
                            1:8192,  # +- 4g
                            2:4096,  # +- 8g
                            3:2048}  # +- 16g
        full_scale = self.full_scale
        accel_raw = self.accel_raw
        conversion = full_scale_table[full_scale]
        return(accel_raw[0]/conversion,accel_raw[1]/conversion,accel_raw[2]/conversion)
    
    # OUT_ADC
    # The lis3dh breakout board has SMD jumpers fixing ADC1 and ADC3 to GND and ADC2 to Vcc.
    # These jumpers must be removed to make the ADC work
    @property    
    def get_ADC1_raw(self):
        #return self.read_word(LIS3DH_OUT_ADC1_L)
        tmp = bytearray(2)
        tmp[0] = self.read_byte(LIS3DH_OUT_ADC1_L)
        tmp[1] = self.read_byte(LIS3DH_OUT_ADC1_H)
        print("ADC1: high 0x{:02x}, low 0x{:02x}".format(tmp[1],tmp[0]))
        return struct.unpack('<h',tmp)[0]
    @property    
    def get_ADC2_raw(self):
        tmp = bytearray(2)
        tmp[0] = self.read_byte(LIS3DH_OUT_ADC2_L)
        tmp[1] = self.read_byte(LIS3DH_OUT_ADC2_H)
        print("ADC2: high 0x{:02x}, low 0x{:02x}".format(tmp[1],tmp[0]))
        return struct.unpack('<h',tmp)[0]
        #return self.read_word(LIS3DH_OUT_ADC2_L)
    @property
    def get_ADC3_raw(self):
        tmp = bytearray(2)
        tmp[0] = self.read_byte(LIS3DH_OUT_ADC3_L)
        tmp[1] = self.read_byte(LIS3DH_OUT_ADC3_H)
        print("ADC3: high 0x{:02x}, low 0x{:02x}".format(tmp[1],tmp[0]))
        return struct.unpack('<h',tmp)[0]
        #return self.read_word(LIS3DH_OUT_ADC3_L)
    @property
    def temperature_reference(self) :
        return self.temperature_calib
    @temperature_reference.setter
    def temperature_reference(self,temp_ref) :
        # the lis3dh only gives relative temperature changes with respect to an undefined reference
        # we measure the temperature with a different sensor and use the measured value as reference
        self.temperature_calib = temp_ref
        
    @property
    def raw_temperature(self):       
        tmp = bytearray(2)
        tmp[0] = self.read_byte(LIS3DH_OUT_ADC3_L)
        tmp[1] = self.read_byte(LIS3DH_OUT_ADC3_H)
        # print("temperature: high 0x{:02x}, low 0x{:02x}".format(tmp[1],tmp[0]))
        
        # print("temp 10 bits: 0x{:02x}{:02x}".format(tmp[1],tmp[0]))
        temp = tmp[1]
        # print("temp: {:08b}".format(temp))
        
        if temp & 0x80 : # check sign bit
            # print("Convert to negative integer")
            # print("temp: {:08b}".format(temp))
            temp = ~temp 
            # print("temp: {:08b}".format(temp))
            temp = -((temp & 0x7f) + 1)
        return temp
    @property
    def temperature(self):
        return self.raw_temperature + self.temperature_calib

    # FIFO_CTRL_REG
    @property
    def fifo_ctrl_reg(self) :
        return self.read_byte(LIS3DH_FIFO_CTRL_REG)
    @fifo_ctrl_reg.setter
    def fifo_ctrl_reg(self, value) :
        self.write_byte(LIS3DH_FIFO_CTRL_REG,value)
    @property
    def fifo_mode(self) :
        return self.get_bits(LIS3DH_FIFO_CTRL_REG, FIFO_MODE_POS, FIFO_MODE_SIZE)
    @fifo_mode.setter
    def fifo_mode(self,value) :
        self.set_bits(LIS3DH_FIFO_CTRL_REG, FIFO_MODE_POS, FIFO_MODE_SIZE,value)
    @property
    def fifo_trigger(self) :
        return self.get_bit(LIS3DH_FIFO_CTRL_REG, FIFO_TRIGGER_SELECT)
    @fifo_trigger.setter
    def fifo_trigger(self) :
        self.set_bit(LIS3DH_FIFO_CTRL_REG, FIFO_TRIGGER_SELECT)
    @property
    def fifo_threshold(self) :
        return self.get_bits(LIS3DH_FIFO_CTRL_REG, FIFO_THRESHOLD_POS, FIFO_THRESHOLD_SIZE)
    @fifo_threshold.setter
    def fifo_threshold(self,value) :
         self.set_bits(LIS3DH_FIFO_CTRL_REG, FIFO_THRESHOLD_POS, FIFO_MODE_THRESHOLD,value)

    def print_fifo_mode(self,fifo_mode) :
        fifo_modes = {FIFO_BYPASS : "Bypass",
                      FIFO_MODE_FIFO: "FIFO",
                      FIFO_MODE_STREAM: "Stream",
                      FIFO_MODE_STREAM_TO_FIFO: "Stream to FIFO"}
        return fifo_modes[fifo_mode]
    
    def clear_fifo(self):
        tmp = self.accel_raw                # dummy read, clears the data available and overrun flags
        current_fifo_mode = self.fifo_mode
        self.fifo_mode = FIFO_BYPASS
        while not self.fifo_no_of_samples == 0 :
            tmp = self.accel_raw
        self.fifo_mode = current_fifo_mode
            
    # FIFO_SRC_REG
    @property
    def fifo_src_reg(self) :
        return self.read_byte(LIS3DH_FIFO_SRC_REG)
    @property
    def fifo_watermark(self) :
        return self.get_bit(LIS3DH_FIFO_SRC_REG, FIFO_WATERMARK)
    @property
    def fifo_overrun(self) :
        return self.get_bit(LIS3DH_FIFO_SRC_REG, FIFO_OVERRUN)
    @property
    def fifo_empty(self) :
        return self.get_bit(LIS3DH_FIFO_SRC_REG, FIFO_EMPTY)
    @property
    def fifo_no_of_samples(self) :
        return self.get_bits(LIS3DH_FIFO_SRC_REG, FIFO_NO_OF_SAMPLES_POS,FIFO_NO_OF_SAMPLES_SIZE)

    # INT1_CFG
    @property
    def int1_cfg(self) :
        return self.read_byte(LIS3DH_INT1_CFG)
    @int1_cfg.setter
    def int1_cfg(self, value) :
        self.write_byte(LIS3DH_FIFO_INT1_CFG,value)
    @property
    def int1_aoi(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_AOI)
    @int1_aoi.setter
    def int1_aoi(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_AOI, value)
    @property 
    def int1_6d(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_6D)
    @int1_6d.setter
    def int1_6d(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_6D, value)
    @property
    def int1_zhie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_ZHIE)
    @int1_zhie.setter
    def set_int1_zhie(self,value) :
        set_bit(LIS3DH_INT1_CFG, INT1_ZHIE, value)
    @property
    def int1_zlie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_ZLIE)
    @int1_zlie.setter
    def int1_zlie(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_ZLIE, value)
    @property
    def int1_yhie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_YHIE)
    @int1_yhie.setter
    def int1_yhie(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_YHIE, value)
    @property
    def int1_ylie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_YLIE)
    @int1_ylie.setter
    def int1_ylie(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_YLIE, value)
    @property
    def int1_xhie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_XHIE)
    @int1_xhie.setter
    def int1_xhie(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_YHIE, value)
    @property
    def int1_xlie(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_XLIE)
    @int1_xlie.setter
    def int1_xlie(self,value) :
        self.set_bit(LIS3DH_INT1_CFG, INT1_XLIE, value)
         
    # INT1_SRC
    @property
    def int1_src(self) :
        return self.read_byte(LIS3DH_INT1_SRC)
    @property
    def int1_src_ia(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_IA)
    @property
    def int1_src_zh(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_ZH)
    @property
    def int1_src_zl(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_ZL)
    @property    
    def int1_src_yh(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_YH)
    @property    
    def int1_src_yl(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_YL)
    @property    
    def int1_src_xh(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_XH)
    @property    
    def int1_src_xl(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_XL)
    
    # INT1_THS 
    @property
    def int1_ths(self) :
        return self.read_byte(LIS3DH_INT1_THS)
    @int1_ths.setter
    def int1_ths(self,value) :
        self.write_byte(LIS3DH_INT1_THS,value)

    # INT1_DURATION
    @property
    def int1_duration(self) :
        return self.read_byte(LIS3DH_INT1_DURATION)
    @int1_duration.setter
    def int1_duration(self,value) :
        self.write_byte(LIS3DH_INT1_DURATION,value)

    # INT2_CFG
    @property
    def int2_cfg(self) :
        return self.read_byte(LIS3DH_INT2_CFG)
    @int2_cfg.setter
    def int2_cfg(self, value) :
        self.write_byte(LIS3DH_FIFO_INT2_CFG,value)
    @property
    def int2_aoi(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_AOI)
    @int2_aoi.setter
    def int2_aoi(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_AOI, value)
    @property
    def int2_6d(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_6D)
    @int2_6d.setter 
    def int2_6d(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_6D, value)
    @property
    def int2_zhie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_ZHIE)
    @int2_zhie.setter
    def set_int2_zhie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_ZHIE, value)
    @property     
    def int2_zlie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_ZLIE)
    @int2_zlie.setter
    def int2_zlie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_ZLIE, value)
    @property
    def int2_yhie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_YHIE)
    @int2_yhie.setter
    def int2_yhie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_YHIE, value)
    @property
    def int2_ylie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_YLIE)
    @int2_ylie.setter
    def int2_ylie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_YLIE, value)
    @property
    def int2_xhie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_XHIE)
    @int2_xhie.setter
    def int2_xhie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_YHIE, value)
    @property
    def int2_xlie(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_XLIE)
    int2_xlie.setter
    def int2_xlie(self,value) :
        self.set_bit(LIS3DH_INT2_CFG, INT2_XLIE, value)
         
    # INT2_SRC
    @property
    def int2_src(self) :
        return self.read_byte(LIS3DH_INT2_SRC)
    @property
    def int2_src_ia(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_IA)
    @property
    def int2_src_zh(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_ZH)
    @property    
    def int2_src_zl(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_ZL)
    @property    
    def int2_src_yh(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_YH)
    @property    
    def int2_src_yl(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_YL)
    @property    
    def int2_src_xh(self) :
        return self.get_bit(LIS3DH_INT2_CFG, INT2_SRC_XH)
    @property    
    def int1_src_xl(self) :
        return self.get_bit(LIS3DH_INT1_CFG, INT1_SRC_XL)

    # INT2_THS 
    @property    
    def int2_ths(self) :
        return self.read_byte(LIS3DH_INT2_THS)
    @int2_ths.setter
    def int2_ths(self,value) :
        self.write_byte(LIS3DH_INT2_THS,value)

    # INT1_DURATION
    @property
    def int2_duration(self) :
        return self.read_byte(LIS3DH_INT2_DURATION)
    @int2_duration.setter
    def int2_duration(self,value) :
        self.write_byte(LIS3DH_INT2_DURATION,value)

    # CLICK_CFG
    @property
    def click_cfg(self) :
        return self.read_byte(LIS3DH_CLICK_CFG)
    @click_cfg.setter
    def click_cfg(self,value) :
        self.write_byte(LIS3DH_CLICK_CFG,value)   
    @property
    def click_zd(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_ZD)
    @click_zd.setter
    def click_zd(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_ZD, value)
    @property
    def click_zs(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_ZS)
    @click_zs.setter
    def click_zs(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_ZS, value)
    @property
    def click_yd(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_YD)
    @click_yd.setter
    def click_yd(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_YD, value)
    @property
    def click_ys(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_YS)
    @click_ys.setter
    def click_ys(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_YS, value)
    @property
    def click_xd(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_XD)
    @click_xd.setter
    def click_xd(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_XD, value)
    @property
    def click_xs(self) :
        return self.get_bit(LIS3DH_CLICK_CFG, CLICK_XS)
    @click_xs.setter
    def set_click_xs(self,value) :
        self.set_bit(LIS3DH_CLICK_CFG, CLICK_XS, value)
         
    # CLICK_SRC
    @property
    def click_src(self) :
        return self.read_byte(LIS3DH_CLICK_SRC)
    @click_src.setter
    def click_src(self,value) :
        self.write_byte(LIS3DH_CLICK_SRC,value)   
    @property
    def click_src_ia(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_IA)
    @click_src_ia.setter
    def click_src_ia(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_IA, value)
    @property
    def click_src_dclick(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_DCLICK)
    @click_src_dclick.setter
    def click_src_dclick(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_DCLICK, value)
    @property
    def click_src_sclick(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_SCLICK)
    @click_src_sclick.setter
    def click_src_sclick(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_SCLICK, value)
    @property
    def click_src_sign(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_SIGN)
    @click_src_sign.setter
    def click_src_sign(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_SIGN, value)
    @property
    def click_src_z(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_Z)
    @click_src_z.setter
    def click_src_z(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_Z, value)
    @property
    def click_src_y(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_Y)
    @click_src_y.setter
    def click_src_y(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_Y, value)
    @property
    def click_src_x(self) :
        return self.get_bit(LIS3DH_CLICK_SRC, CLICK_SRC_X)
    @click_src_x.setter
    def click_src_x(self,value) :
        self.set_bit(LIS3DH_CLICK_SRC, CLICK_SRC_X, value)

    # CLICK_THS
    @property
    def click_ths(self) :
        return self.read_byte(LIS3DH_CLICK_THS)
    @click_ths.setter
    def click_ths(self,value) :
        self.write_byte(LIS3DH_CLICK_THS,value)          
    @property
    def lir_click(self) :
         return self.get_bit(LIS3DH_CLICK_THS, LIR_CLICK)
    @lir_click.setter
    def lir_click(self,value) :
         self.set_bit(LIS3DH_CLICK_SRC, LIR_CLICK, value)
    @property
    def click_threshold(self) :
         return self.get_bits(LIS3DH_CLICK_THS, CLICK_THRESHOLD_POS, CLICK_THRESHOLD_SIZE)
    @click_threshold.setter
    def click_threshold(self,value) :
         self.set_bit(LIS3DH_CLICK_THS, CLICK_THRESHOLD_POS, CLICK_THRESHOLD_SIZE, value)

    # TIME_LIMIT
    @property
    def time_limit(self) :
        return self.read_byte(LIS3DH_TIME_LIMIT)
    @time_limit.setter
    def time_limit(self,value) :
        self.write_byte(LIS3DH_TIME_LIMIT,value)     

    # TIME_LATENCY
    @property
    def time_latency(self) :
        return self.read_byte(LIS3DH_TIME_LATENCY)
    @time_latency.setter
    def time_latency(self,value) :
        self.write_byte(LIS3DH_TIME_LATENCY,value)     

    # TIME_WINDOW
    @property
    def time_window(self) :
        return self.read_byte(LIS3DH_TIME_WINDOW)
    @time_window.setter
    def time_window(self,value) :
        self.write_byte(LIS3DH_TIME_WINDOW,value)
        
    # ACT_THS
    @property
    def activation_threshold(self) :
        return self.read_byte(LIS3DH_ACT_THS)
    @activation_threshold.setter
    def activation_threshold(self,value) :
        self.write_byte(LIS3DH_ACT_THS,value)
        
    # ACT_DUR
    @property
    def activation_duration(self) :
        return self.read_byte(LIS3DH_ACT_DUR)
    @activation_duration.setter
    def activation_duration(self,value) :
        self.write_byte(LIS3DH_ACT_DUR,value)
        

    
   
