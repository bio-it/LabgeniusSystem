###############################################################################
# sc18is602b.py
# I2C - SPI converter for L6470 stepper driver
###############################################################################
import math

###################################
# definitions
###################################
FUNC_ID_CONFIG_SPI_IF = 0xf0
CONFIG_SPI_IF_VALUE = 0x08  # CPOL=1, CPHA=0
FUNC_ID_RW_WR_SPI_0 = 0x01


###############################################################################
# I2C-SPI chip interface class
###############################################################################
class SC18IS602B(object):
    def __init__(self, i2c, i2c_address=0x28):
        self.i2c = i2c
        self.i2c_address = i2c_address
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_CONFIG_SPI_IF, CONFIG_SPI_IF_VALUE)

    ###################################
    # interface
    # - xfer_cmd(cmd)
    # - xfer_param(value, bitlen)
    ###################################
    def xfer_cmd(self, cmd):
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_RW_WR_SPI_0, cmd)
        return self.i2c.read_byte(self.i2c_address)
    def xfer_byte(self, value):
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_RW_WR_SPI_0, value)
        return self.i2c.read_byte(self.i2c_address)
    def convert_to_bytes(self, val, size, signed=True):
        return val.to_bytes(size, byteorder="big", signed=signed)
    def xfer_param(self, value, bitlen):
        bytelen = math.ceil(bitlen/8)
        ret_value = 0x00000000
        pay_load = self.convert_to_bytes(value, bytelen)
        for i in range(bytelen):
            ret_value <<= 8
            temp = self.xfer_byte(pay_load[i])
            ret_value |= temp
        mask = 0xffffffff >> (32 - bitlen)
        return ret_value & mask
#class SC18IS602B
#sc18is602b.py
