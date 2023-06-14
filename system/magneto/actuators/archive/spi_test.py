import math
import time
import spidev

def spi_xfer(spi, bytedata):
    temp = spi.xfer2([bytedata])
    return temp[0]

def spi_xfer_bytes(spi, value, bitlen, byteorder="big", signed=False):
    bytelen = math.ceil(bitlen/8)
    ret_value = 0x00000000
    pay_load = value.to_bytes(bytelen, byteorder=byteorder, signed=signed)
    for data in pay_load:
        ret_value <<= 8
        temp = spi_xfer(spi, data)
        ret_value |= temp
    mask = 0xffffffff >> (32 - bitlen)
    return ret_value & mask

def init_spi(bus, device, mode):
    spi = spidev.SpiDev()
    spi.open(bus, device)
    spi.max_speed_hz = 1000000
    spi.mode = mode
    spi.lsbfirst = False
    return spi

if __name__ == '__main__':
    try:
        # chamber spi test
        # device = 2 (gpio 17)
        # L6470 spi mode = 3
        spi_chamber = init_spi(0, 2, 3)
        L6470_CONFIG = 0x18
        L6470_GET_PARAM = 0x20
        L6470_SET_PARAM = 0x00

        pay_load = L6470_CONFIG | L6470_GET_PARAM;
        spi_xfer(spi_chamber, pay_load)
        L6470_CONFIG_BITLEN = 16
        config_value = spi_xfer_bytes(spi_chamber, 0, L6470_CONFIG_BITLEN)
        print(hex(config_value))

        pay_load = L6470_CONFIG | L6470_GET_PARAM;
        spi_xfer(spi_chamber, pay_load)
        L6470_CONFIG_BITLEN = 16
        config_value = spi_xfer_bytes(spi_chamber, 0, L6470_CONFIG_BITLEN)
        print(hex(config_value))

        pay_load = L6470_CONFIG | L6470_SET_PARAM;
        spi_xfer(spi_chamber, pay_load)
        L6470_CONFIG_BITLEN = 16
        spi_xfer_bytes(spi_chamber, config_value, L6470_CONFIG_BITLEN)

        pay_load = L6470_CONFIG | L6470_GET_PARAM;
        spi_xfer(spi_chamber, pay_load)
        L6470_CONFIG_BITLEN = 16
        config_value = spi_xfer_bytes(spi_chamber, 0, L6470_CONFIG_BITLEN)
        print(hex(config_value))

        # optic spi test
        # device = 3 (gpio 27)
        # L6470 spi mode = 3
        spi_optic = init_spi(0, 3, 3) # L6470 spi mode = 3
        L6470_CONFIG = 0x18
        L6470_GET_PARAM = 0x20
        pay_load = L6470_CONFIG | L6470_GET_PARAM;
        spi_xfer(spi_optic, pay_load)
        L6470_CONFIG_BITLEN = 16
        pay_load = 0;
        config_value = spi_xfer_bytes(spi_optic, pay_load, L6470_CONFIG_BITLEN)
        print(hex(config_value))

        # syringe spi test
        # device = 4 (gpio 22)
        # arduino pro-micro spi mode = 0
        spi_syringe = init_spi(0, 4, 0)
        # print(spi_xfer(spi_syringe, 0))
        # print(spi_xfer(spi_syringe, 1))
        # print(spi_xfer(spi_syringe, 2))
        target_position = 200;
        spi_xfer(spi_syringe, 0)
        current_position = spi_xfer_bytes(spi_syringe, target_position, 16)
        print(current_position)

    except (KeyboardInterrupt, SystemExit):
        print('\nReceived keyboard interrupt, quitting threads.\n')
        g_is_accepted = False
