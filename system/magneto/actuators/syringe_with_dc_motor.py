# -*- coding: utf-8 -*-
###############################################################################
# syringe_emulator.py
###############################################################################
from time import sleep
import time
import math
import spidev

def spi_xfer(spi, bytedata):
    temp = spi.xfer2([bytedata])
    return temp[0]

def spi_xfer_bytes(spi, value, bitlen, byteorder="little", signed=False):
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


class StopRequestException(Exception):
    pass


class BusyClearException(Exception):
    pass


class Syringe():
    def __init__(self):
        self.stop_request = False
        self.min_position = 0  # mm
        self.max_position = 100  # mm
        self.min_adc = 0  # potentiomenter
        self.max_adc = 1023  # potentiomenter
        self.speed = 10  # 10 mm / 1 s
        self.current_position = 0  # mm
        self.last_time = time.time()
        self.home_position = 10  # mm
        self.jog_shift = 10.0  # mm
        #
        self.stop_request = False
        #
        # device = 4 (gpio 22)
        # arduino pro-micro spi mode = 0
        self.spi = init_spi(0, 4, 0)
        #
        self._start(self.home_position)
        sleep(1)
        print('Syringe initialized')

    def _check_busy(self):
        if time.time() >= self.busy_end_time:
            raise BusyClearException

    def _check_stop_request(self):
        if self.stop_request:
            self.stop_request = False
            raise StopRequestException

    def home(self):
        print('syringe.home')
        self._move_to(self.home_position)

    def position(self, position):
        print(f"syringe.position", position)
        self._move_to(position)

    def volume(self, volume):
        print(f"syringe.volume", volume)
        self._move_to(volume)

    def stop(self):
        print(f"syringe.stop")
        self.stop_request = True

    # interpolate motion
    def wait(self):
        # check stop request
        if self.stop_request:
            self.stop_request = False
            return False  # finished
        # calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        # calculate delta postion
        delta_position = self.speed * delta_time
        # calculate next position
        if self.direction == '+':
            next_position = self.current_position + delta_position
            if next_position >= self.target_position:
                next_position = self.target_position
        else:
            next_position = self.current_position - delta_position
            if next_position <= self.target_position:
                next_position = self.target_position
        # update current position
        self.current_position = next_position
        # set waiting return flag
        waiting = True  # keep waiting
        if self.direction == '+':
            if next_position >= self.target_position:
                waiting = False
        else:
            if next_position <= self.target_position:
                waiting = False  # finished
        # # output pwm
        # pulse_width = self._mm_to_pulsewidth(self.current_position)
        # self.pwm.set_servo_pulsewidth(self.bcm_pin, pulse_width)
        # output to spi
        adc_value = self._mm_to_adc(self.current_position)
        spi_xfer(self.spi, 0)
        current_position = spi_xfer_bytes(self.spi, adc_value, 16)
        # return
        return waiting

    #######################################
    # private functions
    #######################################
    def _mm_to_adc(self, mm):
        return int((mm - self.min_position)
                   * (self.max_adc - self.min_adc)
                   / (self.max_position - self.min_position)
                   + self.min_adc)

    # start from initial unkown position
    def _start(self, target_pos):
        self.current_pos = target_pos
        adc_value = self._mm_to_adc(target_pos)
        spi_xfer(self.spi, 0)
        current_position = spi_xfer_bytes(self.spi, adc_value, 16)
        self.last_time = time.time()

    def _move_to(self, target_position):
        if target_position > self.max_position:
            target_position = self.max_position
        if target_position < self.min_position:
            target_position = self.min_position
        self.target_position = target_position
        self.last_time = time.time()
        if self.current_pos < target_position:
            self.direction = '+'
        else:
            self.direction = '-'




# syringe_emulator.py
