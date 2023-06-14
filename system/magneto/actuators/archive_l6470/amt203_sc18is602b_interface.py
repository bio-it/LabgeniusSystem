###############################################################################
# amt203_sc18is602b_interface.py
# I2C - SPI converter for AMT203 abs encoder
###############################################################################
import math

###################################
# definitions
###################################
FUNC_ID_CONFIG_SPI_IF = 0xf0
CONFIG_SPI_IF_VALUE = 0x00  # CPOL=0, CPHA=0
FUNC_ID_RW_WR_SPI_0 = 0x01


###############################################################################
# I2C-SPI chip interface class
###############################################################################
class Amt203Sc18is602bInterface(object):
    def __init__(self, i2c, i2c_address=0x28):
        self.i2c = i2c
        self.i2c_address = i2c_address
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_CONFIG_SPI_IF, CONFIG_SPI_IF_VALUE)

    ###################################
    # interface
    # - xfer_cmd(cmd)
    ###################################
    def xfer_cmd(self, bytedata):
        self.i2c.write_byte_data(self.i2c_address, FUNC_ID_RW_WR_SPI_0, bytedata)
        return self.i2c.read_byte(self.i2c_address)

#class Amt203Sc18is602bInterface


#Amt203Sc18is602bInterface.py
