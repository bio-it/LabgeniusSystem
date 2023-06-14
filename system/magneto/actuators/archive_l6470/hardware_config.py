# -*- coding: utf-8 -*-
###############################################################################
# hardware_config.py
###############################################################################
# emulator = True
emulator = False
if emulator:
    #######################################
    # emulator configuration
    #######################################
    # from magneto.actuators.magnet_emulator import MagnetEmulator
    # from magneto.actuators.syringe_emulator import SyringeEmulator
    # from magneto.actuators.chamber_emulator import ChamberEmulator
    # from magneto.actuators.filter_emulator import FilterEmulator
    # chamber = ChamberEmulator()
    # syringe = SyringeEmulator()
    # magnet = MagnetEmulator()
    # filter = FilterEmulator()

else:
    #######################################
    # physical configuration
    #######################################
    import spidev
    # import smbus
    # from magneto.actuators.l6470_sc18is602b_interface import L6470Sc18is602bInterface
    # from magneto.actuators.amt203_sc18is602b_interface import Amt203Sc18is602bInterface
    # from magneto.actuators.amt203 import AMT203
    # from magneto.actuators.chamber import Chamber
    # from magneto.actuators.syringe import Syringe
    # from magneto.actuators.filter import Filter
    # from magneto.actuators.magnet import Magnet
    # from time import sleep

    # i2c = smbus.SMBus(1)
    # sleep(1)  # wait here to avoid i2i IO Error

    # i2c_address = (0b0101000 | 0b011)  # J1 on HAT board
    # spi = Amt203Sc18is602bInterface(i2c, i2c_address)
    # chamber_encoder = AMT203(spi)

    # i2c_address = (0b0101000 | 0b100)  # J3 on HAT board
    # spi = Amt203Sc18is602bInterface(i2c, i2c_address)
    # syringe_encoder = AMT203(spi, reverse_dir=True)

    # i2c_address = (0b0101000 | 0b000)  # JP12 on HAT board
    # spi = L6470Sc18is602bInterface(i2c, i2c_address)
    # chamber = Chamber(spi, chamber_encoder)

    # i2c_address = (0b0101000 | 0b001)  # JP10 on HAT board
    # spi = L6470Sc18is602bInterface(i2c, i2c_address)
    # syringe = Syringe(spi, syringe_encoder)

    # i2c_address = (0b0101000 | 0b010)  # JP8 on HAT board
    # spi = L6470Sc18is602bInterface(i2c, i2c_address)
    # filter = Filter(spi)

    # magnet = Magnet(18)  # pigpio, Physical pin 12 _ BCM 18 (PWM0)

# hardware_config.py
