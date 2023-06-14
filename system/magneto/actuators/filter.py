# -*- coding: utf-8 -*-
###############################################################################
# filter.py
###############################################################################
import magneto.actuators.tmc5130 as tmc5130
from magneto.actuators.tmc5130_stepper import TMC5130Stepper
from time import sleep


class Filter(TMC5130Stepper):
  ###################################
  # __init__
  ###################################
  def __init__(self, spi):
    print('filter class')
    super().__init__(spi)
    super().stop() # clears stop left and right on power-up

    # 1110 0110 0x60 CHOPCONF
    # SPI send: 0xEC000100C3; // CHOPCONF: TOFF=3, HSTRT=4, HEND=1, TBL=2, CHM=0 (SpreadCycle)
    super().set_register(tmc5130.CHOPCONF, 0x000100C3)
    # 1001 0001 0x10 IHOLD_RUN
    # SPI send: 0x9000061F0A; // IHOLD_IRUN: IHOLD=10, IRUN=31 (max. current), IHOLDDELAY=6
    super().set_ihold(5) # 3
    super().set_irun(20) # 10 <- 6
    super().set_iholddelay(6)
    # 1001 0001 0x11 TPOWERDOWN
    # SPI send: 0x910000000A; // TPOWERDOWN=10: Delay before power down in stand still
    super().set_register(tmc5130.TPOWERDOWN, 0x0000000A)
    # 1000 0000 0x00 GCONF
    # SPI send: 0x8000000004; // EN_PWM_MODE=1 enables StealthChop (with default PWMCONF)
    super().set_register(tmc5130.GCONF, 0x00000004)
    # 1001 0001 0x13 TPWM_THRS
    # SPI send: 0x93000001F4; // TPWM_THRS=500 yields a switching velocity about 35000 = ca. 30RPM
    super().set_register(tmc5130.TPWMTHRS, 500)
    # 1111 0111 0x70 PWMCONF
    # SPI send: 0xF0000401C8; // PWMCONF: AUTO=1, 2/1024 Fclk, Switch amplitude limit=200, Grad=1
    super().set_register(tmc5130.PWMCONF, 0x000401C8)

    # # GCONF
    # super().set_register(0x00, 0x00000000)
    # # CHOPCONF: TOFF=5, HSTRT=5, HEND=3, TBL=2, CHM=0 (spreadcycle)
    # super().set_register(0x6C, 0x000101D5)
    # # # IHOLD_IRUN: IHOLD=3, IRUN=6 (max.current?), IHOLDDELAY=7
    # # super().set_register(0x10, 0x00070603)
    # # super().set_ihold(10) # noisy
    # # super().set_irun(20) # 10 <- 6
    # # super().set_iholddelay(7)
    # super().set_ihold(3) # 3
    # super().set_irun(10) # 10 <- 6
    # super().set_iholddelay(7)
    # # TPOWERDOWN=10
    # super().set_register(0x11, 0x0000000A)
    # # PWMCONF
    # super().set_register(0x70, 0x00000000)
    # # super().set_register(0xF0,0x000401C8); #PWM_CONF: AUTO=1, 2/1024 Fclk, Switch amp limit=200, grad=1

    # steps
    self.motor_step = 200
    self.micro_step = 256
    self.microstepes_per_rev = self.motor_step * self.micro_step

    # speed profile
    self.vmax = 360.0 / 2 # [rev/s]
    self.amax = self.vmax * 10
    vmax = self._deg_to_microsteps(self.vmax)
    amax = self._deg_to_microsteps(self.amax)
    super().set_vstart(10)
    super().set_a1(amax)
    super().set_v1(vmax)
    super().set_amax(amax)
    super().set_vmax(vmax)
    super().set_dmax(amax)
    super().set_d1(amax)
    super().set_vstop(10)
    self.jog_amount_default = 5.0  # [deg]
    self.jog_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s

    # position
    super().set_register(tmc5130.RAMPMODE, 0x00000000)  # RAMPMODE=0
    super().set_register(tmc5130.XACTUAL, 0x00000000)  # XACTUAL=0
    super().set_register(tmc5130.XTARGET, 0x00000000)  # XTARGET=0

    # encoder position - no encoder

    # switch mode
    self._reset_switch_mode()

    # homing
    self.release_switch_speed = 360.0/2 # [deg/s]
    self.search_switch_speed = 360.0/3 # [deg/s], 360.0/2 speed could miss the switch
    self.go_to_switch_latch_position_speed = 360.0/2 # [deg/s]
    self.home_position = 0.0 # [deg]
    self.shift_from_home_speed = 360.0/2 # [deg/s]
    self.shift_from_home_distance = 5.0 # [deg]

    # goto command
    self.min_filter_no = 1
    self.max_filter_no = 4
    self.goto_speed = 360.0/2  # [deg/s], 360 deg in 2 s

  ###################################
  # interface functions
  ###################################
  def get_min_filter_no(self):
      return self.min_filter_no

  def get_max_filter_no(self):
      return self.max_filter_no

  def get_register(self, no):
    return super().get_register(no)
  
  def set_register(self, no, value):
    return super().set_register(no, value)

  def get_pos(self):
    return self._microsteps_to_deg(super().get_xactual())

  def get_latch_pos(self):
    return self._microsteps_to_deg(super().get_xlatch())

  def get_encoder_position(self):
    return 0

  def get_velocity(self):
    return self._microsteps_to_deg(super().get_vactual())  

  def jog(self, direction, amount=None):
    if amount == None:
        amount = self.jog_amount_default
    if direction == '+':
        amount = abs(amount)
    else:
        amount = -abs(amount)
    amount = self._deg_to_microsteps(amount)
    velocity_max = self._deg_to_microsteps(self.jog_speed)
    super().move_by(amount, velocity_max)

  def goto(self, no):
    if no < self.min_filter_no:
      print(f'goto filter no {no} is not valid')
      return
    if no > self.max_filter_no:
      print(f'goto filter no {no} is not valid')
      return
    position = self._no_to_deggree(no)
    print(f'goto():{position}, {self._deg_to_microsteps(position)}')
    position = self._deg_to_microsteps(position)
    velocity_max = self._deg_to_microsteps(self.goto_speed)
    super().move_to(position, velocity_max)

  def position(self, position):
    position = self._deg_to_microsteps(position)
    velocity = self._deg_to_microsteps(self.vmax)
    super().move_to(position, velocity)

  def _no_to_deggree(self, filter_no):
    interval = 360 / self.max_filter_no
    position = interval * (filter_no - 1)
    return position

  def stop(self):
    super().stop()
    self.stop_home()

  def wait(self):
    return super().is_busy()



  ###################################
  # home functions
  ###################################
  def release_switch(self):
    self.stop()
    print('filter.release_switch()')
    print('checking switch')
    # return if not switch on
    super().unswap_switch()
    super().set_left_switch_active_low()
    if not super().is_switch_on():
      print('switch is not on')
      return
    # set condition to detect switch rising edge (high active)
    print('switch is on')
    print(super().is_switch_on())
    print('set switch mode')
    super().swap_switch()
    super().set_right_switch_active_high()
    super().enable_right_switch()
    # move to (+) inf position
    print('moving to + inf')
    position = tmc5130.MAX_POSITION
    # print('moving to - inf')
    # position = tmc5130.MIN_POSITION
    velocity = self._deg_to_microsteps(self.release_switch_speed)
    super().move_to(position, velocity)

  def search_switch(self):
    print('filter.search_switch()')
    self.stop()
    # return if switch is already on
    super().unswap_switch()
    super().set_left_switch_active_low()
    if super().is_switch_on():
      print('switch is already on')
      return
    # set condition to detect switch falling edge
    super().unswap_switch()
    super().set_left_switch_active_low()
    super().enable_left_switch()
    super().set_left_switch_latch_active()
    # move to (-) inf position
    position = tmc5130.MIN_POSITION
    velocity = self._deg_to_microsteps(self.search_switch_speed)
    super().move_to(position, velocity)

  def go_to_switch_latch_position(self):
    print('filter.go_to_switch_latch_position()')
    print(self.get_pos(), self.get_latch_pos())
    position = super().get_xlatch()
    velocity = self._deg_to_microsteps(self.go_to_switch_latch_position_speed)
    super().move_to(position, velocity)

  def set_home_position(self):
    print('filter.set_home_position()')
    position = self._deg_to_microsteps(self.home_position)
    self.set_register(tmc5130.XACTUAL, position)
    self.set_register(tmc5130.XTARGET, position)

  def shift_from_home(self):
    print('filter.shift_from_home()')
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_ENC_X)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    distance = self._deg_to_microsteps(self.shift_from_home_distance)
    velocity = self._deg_to_microsteps(self.shift_from_home_speed)
    super().move_by(distance, velocity)

  # called at the end of home sequence
  def finish_home(self):
    print('filter.finish_home()')
    self._reset_switch_mode()

  # called by user stop
  def stop_home(self):
    self._reset_switch_mode()

  def _reset_switch_mode(self):
    super().set_register(tmc5130.SW_MODE, 0)
    super().enable_soft_switch_stop()
    super().unswap_switch()
    super().set_right_switch_active_low() # right switch is floating
    super().set_left_switch_active_low() # left switch is connected to a low active switch
    super().disable_left_switch()
    super().disable_right_switch()
    super().clear_switch_latches()

  ###################################
  # uint conversion
  ###################################
  def _deg_to_microsteps(self, deg):
    return int(deg * self.microstepes_per_rev / 360.0)
  
  def _microsteps_to_deg(self, microsteps):
    return microsteps * 360.0 / self.microstepes_per_rev


#filter.py
