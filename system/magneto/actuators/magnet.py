# -*- coding: utf-8 -*-
###############################################################################
# magnet.py
###############################################################################
'''
L12 -R Micro Linear Servo - 30mm - 50:1 - 6 vdc
L12-30-50-6-R
1000 us = 0 mm, 2000 us = 30 mm
5% at 50 Hz   , 10% at 50 Hz

# Servo(overrides PWM commands on same GPIO)   #http://abyz.me.uk/rpi/pigpio/python.html
# set_servo_pulsewidth(user_gpio, pulsewidth)
# get_servo_pulsewidth(user_gpio) #Returns the servo pulsewidth being used on the GPIO.
'''
###############################################################################
import pigpio
from time import sleep
import time

###############################################################################
# Magent class
# mandatory functions: on, off, home, wait, stop
###############################################################################


class Magnet:
    #######################################
    # mandatory functions
    #######################################
    def __init__(self, pin):
        self.pwm = pigpio.pi()
        self.pwm.set_servo_pulsewidth(pin, 0)  # pulse off
        self.bcm_pin = pin  # pigpio, Physical pin 12 _ BCM 18 (PWM0)
        self.min_position = 0  # mm
        self.max_position = 30  # mm, L12-30-XX-6-R
        self.min_pulse = 1000  # us, 50Hz
        self.max_pulse = 2000  # us, 50Hz
        # self.speed = 100/15  # 100 mm / 15 s
        self.speed = 30/10  # 30 mm / 10 s

        self.current_position = 0  # mm
        self.target_position = self.current_position  # mm
        self.last_time = time.time()
        self.off_position = 0  # mm
        # self.on_position = 20  # mm
        self.on_position = 20  # mm

        self.home_position = self.current_position  # mm
        # self.jog_shift = 10.0  # mm
        self.jog_shift = 3.0  # mm

        self._start(0)
        sleep(1)

        self.direction = '' # '', '+', '-'
        print('Maget initialized')

    def home(self):
        print('magnet.home')
        self._move_to(self.home_position)

    def on(self):
        print('magnet->on')
        self._move_to(self.on_position)

    def off(self):
        print('magnet->off')
        self._move_to(self.off_position)

    def jog(self, fwd=True):
        if fwd:
            self._move_to(self.current_position + self.jog_shift)
        else:
            self._move_to(self.current_position - self.jog_shift)

    def stop(self):
        print('magnet->stop')
        self.direction = ''

    def shutdown(self):  # Release pigpio resources.
        self.pwm.stop()

    # interpolate motion
    def wait(self):
        if self.direction == '':
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
        # print('magnet.waiting')
        # print(self.direction, next_position, self.target_position)
        if self.direction == '+':
            if next_position >= self.target_position:
                waiting = False
        else:
            if next_position <= self.target_position:
                waiting = False  # finished
        # output pwm
        pulse_width = self._mm_to_pulsewidth(self.current_position)
        self.pwm.set_servo_pulsewidth(self.bcm_pin, pulse_width)
        # return
        return waiting

    def is_busy(self):
        return self.wait()     

    #######################################
    # private functions
    #######################################
    def _mm_to_pulsewidth(self, mm):
        return int((mm - self.min_position)
                   * (self.max_pulse - self.min_pulse)
                   / (self.max_position - self.min_position)
                   + self.min_pulse)

    # start from initial unkown position
    def _start(self, target_pos):
        self.current_position = target_pos
        pulse_width = self._mm_to_pulsewidth(target_pos)
        self.pwm.set_servo_pulsewidth(self.bcm_pin, pulse_width)
        self.last_time = time.time()

    def _move_to(self, target_position):
        if target_position > self.max_position:
            target_position = self.max_position
        if target_position < self.min_position:
            target_position = self.min_position
        self.target_position = target_position
        self.last_time = time.time()
        if self.current_position < target_position:
            self.direction = '+'
        else:
            self.direction = '-'
# magent.py
# E. O. F.


'''
    ## Constant of (class)Magnet
    ## step definitions
    MOTOR_STEPS_PER_REV = 200
    MIRCO_STEP = 128
    ## Linear actuator: 21H4(X)-V -905
    FULL_STROKE_IN_MM = 12.7      # 905
    LINEAR_TRVL_IN_MM_PER_STEP = 0.0121    # J: Linear Travel / Step
    MM_IN_MICRO_STEP = int(1 / LINEAR_TRVL_IN_MM_PER_STEP) * \
        MIRCO_STEP  # 1/0.0121=82.64462809917355
    FULL_STROKE_IN_MICRO_STEP = int(
        FULL_STROKE_IN_MM / LINEAR_TRVL_IN_MM_PER_STEP) * MIRCO_STEP  # 1049.586776859504 Steps
    # shift after release switch to ensure thatn the switch is off enough
    HOME_SHIFT_IN_MICRO_STEP =_IN_MICRO_STEP * 1.0)
    ## Magnet position
    OFF_POS_IN_MM = 2
    MAGNET_OFF_OFFSET_IN_MM = AGNET_ON_OFFSET_IN_MM = -1
  OS_IN_MICRO_STEP = int(
        OFF_POS_IN_MM / LINEAR_TRVL_IN_MM_PER_STEP) * MIRCO_STEP
    MAGNET_OFF_OFFSET_IN_MICRO_STEP = int(
        MAGNET_OFF_OFFSET_IN_MM / LINEAR_TRVL_IN_MM_PER_STEP) * MIRCO_STEP
    MAGNET_ON_OFFSET_IN_MICRO_STEP = int(
        MAGNET_ON_OFFSET_IN_MM / LINEAR_TRVL_IN_MM_PER_STEP) * MIRCO_STEP

    ## speed
    # 2.0 rev/s, motor step unit
    MAGNET_ONOFF_SPEED = int(2.0 * MOTOR_STEPS_PER_REV)
    # 1.0 rev/s, motor step unit
    GO_UNTIL_SPEED = int(1.0 * MOTOR_STEPS_PER_REV)
'''
