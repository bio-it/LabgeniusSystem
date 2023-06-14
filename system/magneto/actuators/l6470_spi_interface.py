###############################################################################
# l6470_spi_interface.py
###############################################################################
import math
import spidev

###############################################################################
# L6470 spi interface class
###############################################################################
class L6470SpiInterface(object):
    def __init__(self, bus, device, mode):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000
        self.spi.mode = mode
        self.spi.lsbfirst = False

    ###################################
    # interface
    # - xfer_cmd(cmd)
    # - xfer_param(value, bitlen)
    ###################################
    def xfer_cmd(self, bytedata):
        temp = self.spi.xfer2([bytedata])
        return temp[0]
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
#class L6470SpiInterface


# l6470_spi_interface.py
