###############################################################################
# l6470_sc18is602b_interface.py
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
class L6470Sc18is602bInterface(object):
    def __init__(self, i2c, i2c_address=0x28):
        self.i2c = i2c
        self.i2c_address = i2c_address
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_CONFIG_SPI_IF, CONFIG_SPI_IF_VALUE)

    ###################################
    # interface
    # - xfer_cmd(cmd)
    # - xfer_param(value, bitlen)
    ###################################
    def xfer_cmd(self, bytedata):
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_RW_WR_SPI_0, bytedata)
        return self.i2c.read_byte(self.i2c_address)
    def xfer_param(self, value, bitlen, byteorder="big", signed=False):
        bytelen = math.ceil(bitlen/8)
        ret_value = 0x00000000
        pay_load = value.to_bytes(bytelen, byteorder=byteorder, signed=signed)
        for data in pay_load:
            ret_value <<= 8
            temp = self.xfer_cmd(data)
            ret_value |= temp
        mask = 0xffffffff >> (32 - bitlen)
        return ret_value & mask
#class L6470Sc18is602bInterface


#L6470Sc18is602bInterface.py
