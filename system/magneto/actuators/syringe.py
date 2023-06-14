# -*- coding: utf-8 -*-
###############################################################################
# syringe.py
###############################################################################
from time import sleep
import math
import magneto.actuators.tmc5130 as tmc5130
from magneto.actuators.tmc5130_stepper import TMC5130Stepper


class Syringe(TMC5130Stepper):
  ###################################
  # __init__
  ###################################
  def __init__(self, spi):
    print('syringe class')
    super().__init__(spi)
    super().stop() # clears stop left and right on power-up

    # 1110 0110 0x60 CHOPCONF
    # SPI send: 0xEC000100C3; // CHOPCONF: TOFF=3, HSTRT=4, HEND=1, TBL=2, CHM=0 (SpreadCycle)
    super().set_register(tmc5130.CHOPCONF, 0x000100C3)
    # 1001 0001 0x10 IHOLD_RUN
    # SPI send: 0x9000061F0A; // IHOLD_IRUN: IHOLD=10, IRUN=31 (max. current), IHOLDDELAY=6
    super().set_ihold(10) # 3
    super().set_irun(20) # 10 <- 6
    super().set_iholddelay(6)
    # 1001 0001 0x11 TPOWERDOWN
    # SPI send: 0x910000000A; // TPOWERDOWN=10: Delay before power down in stand still
    super().set_register(tmc5130.TPOWERDOWN, 0x0000000A)
    # 1000 0000 0x00 GCONF
    # SPI send: 0x8000000004; // EN_PWM_MODE=1 enables StealthChop (with default PWMCONF)
    # super().set_register(tmc5130.GCONF, 0x00000004)
    super().set_register(tmc5130.GCONF, 0)
    super().set_register_bit(tmc5130.GCONF, tmc5130.BIT_GCONF_EN_PWM_MODE) # inverse motor direction
    super().set_register_bit(tmc5130.GCONF, tmc5130.BIT_GCONF_SHAFT) # inverse motor direction
    # 1001 0001 0x13 TPWM_THRS
    # SPI send: 0x93000001F4; // TPWM_THRS=500 yields a switching velocity about 35000 = ca. 30RPM
    # super().set_register(tmc5130.TPWMTHRS, 500)
    super().set_register(tmc5130.TPWMTHRS, 6000)
    # 1111 0111 0x70 PWMCONF
    # SPI send: 0xF0000401C8; // PWMCONF: AUTO=1, 2/1024 Fclk, Switch amplitude limit=200, Grad=1
    super().set_register(tmc5130.PWMCONF, 0x000401C8)

    # # GCONF
    # super().set_register(0x00, 0x00000000)
    # super().set_register_bit(tmc5130.GCONF, tmc5130.BIT_GCONF_SHAFT) # inverse motor direction
    # # CHOPCONF: TOFF=5, HSTRT=5, HEND=3, TBL=2, CHM=0 (spreadcycle)
    # super().set_register(0x6C, 0x000101D5)
    # # # IHOLD_IRUN: IHOLD=3, IRUN=6 (max.current?), IHOLDDELAY=7
    # # super().set_register(0x10, 0x00070603)
    # super().set_ihold(3)
    # super().set_irun(10)
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
    
    # ball screw lead
    self.lead = 1.0 # [mm]

    # speed profile
    self.vmax = 5.0 # [mm/s]
    self.amax = self.vmax * 10 # [mm/s/s] 0.1 s to max speed
    vmax = self._mm_to_microsteps(self.vmax)
    amax = self._mm_to_microsteps(self.amax)
    super().set_vstart(10)
    super().set_a1(amax)
    super().set_v1(vmax)
    super().set_amax(amax)
    super().set_vmax(vmax)
    super().set_dmax(amax)
    super().set_d1(amax)
    super().set_vstop(10)
    
    # jog
    self.jog_amount_def = 3.0 # [mm]
    self.jog_speed = 5.0 # [mm/s]

    # position
    super().set_register(tmc5130.RAMPMODE, 0x00000000)  # RAMPMODE=0
    super().set_register(tmc5130.XACTUAL, 0x00000000)  # XACTUAL=0
    super().set_register(tmc5130.XTARGET, 0x00000000)  # XTARGET=0

    # switch mode
    super().set_register(tmc5130.SW_MODE, 0)
    super().set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_EN_SOFTSTOP)
    super().set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_L)
    # super().set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_R)
    super().set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_STOP_L_ENABLE)
    super().set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_LATCH_L_ACTIVE)

    # encoder setting
    super().set_register(tmc5130.X_ENC, 0)
    super().set_encoder_n_signal_high_active()
    super().ignore_ab_for_encoder_n_signal()
    super().set_encoder_n_signal_event_rising_edge()
    self._reset_encoder_mode()
    # (case 1) amt112S: default 400 x 4 ppr, 0.3 deg resolution vs 0.2 deg encoder accuracy
    # encode constant mode is binary mode by deafualt
    # driver usteps/rev = 200 motorsteps/rev x 256 usteps/motorstep = 51200 usteps/rev
    # encode pulses/rev = 400x4 pulses/rev x const
    # const = (51200 / 1600) = 32 = (2^5 * 2^16) | 0000/2^16)
    # super().set_register(tmc5130.ENC_CONST, (1<<21))
    # (case 2) amt112s: setting 1600 x 4 ppr, 0.056 deg resolution vs 0.2 deg encoder accuarcy
    # encode constant mode is binary mode by deafualt
    # driver usteps/rev = 200 motorsteps/rev x 256 usteps/motorstep = 51200 usteps/rev
    # encode pulses/rev = 1600x4 pulses/rev x const
    # const = (51200 / 6400) = 8 = (2^3 * 2^16) | 0000/2^16)
    # super().set_register(tmc5130.ENC_CONST, (1<<19))
    # (case 3) amt203: deafult 1024 x 4 ppr, 0.088 deg resolution vs 0.2 deg encoder accuarcy
    # driver usteps/rev = 200 motorsteps/rev x 256 usteps/motorstep = 51200 usteps/rev
    # encode pulses/rev = 1024x4 pulses/rev x const
    # const = (51200 / 4096) = 12.5 = (12 * 2^16) | (5000/10000)
    # (case 4) amt203: deafult 1024 x 4 ppr, 0.088 deg resolution vs 0.2 deg encoder accuarcy
    #        + syringe driver direction is inversed 
    # driver usteps/rev = 200 motorsteps/rev x 256 usteps/motorstep = 51200 usteps/rev
    # encode pulses/rev = 1024x4 pulses/rev x const
    # const = -(51200 / 4096) = -12.5 = -13 + 0.5 = (-13 * 2^16) | (5000/10000)
    super().set_encoder_select_decimal()
    super().set_register(tmc5130.ENC_CONST, (((-13*(1<<16)) | (5000))))

    # homing
    self.release_switch_speed = 5.0 # 5.0 # [mm/s]
    self.search_switch_speed = 5.0 # 5.0 # [mm/s]
    self.go_to_switch_latch_position_speed = 5.0 # [mm/s]
    self.search_encoder_n_signal_speed = 5.0 # 5.0 # [mm/s]
    self.search_encoder_n_signal_distance = 1.1 # [mm/s]
    self.go_back_to_encoder_n_signal_speed = 5.0 # 5.0/2 # [mm/s]
    self.home_position = 0.0 # [mm]
    self.shift_from_home_speed = 5.0/2 # [mm/s]
    self.shift_from_home_distance = 1.0 # [mm]

    '''
    mechanical considerations:
    - (+) direction is downwards and (-) direction is upwards
    - problem: home siwtch is paced at a too high position
    -- after go_until, (-) upwards 2 mm shift is needed to load the cartridge
       at this position, there is (-) 3 mm margin.
    -- home go_until: (-)
    '''
    # mechanical properties
    self.bottom_pos_def = 51.0  # [mm]
    self.bottom_pos = self.bottom_pos_def
    self.top_pos = 0.0
    self.disk_radius = 3.0  # [mm]

    # pumping speed
    # self.pumping_speed = 6.25  # [mm/s]
    self.pumping_speed = 5.0  # [mm/s]
    self.slow_pumping_speed = 1.25  # [mm/s]

    # self.save_offset_position()
    self._load_bottom_position()


  ###################################
  # interface functions
  ###################################
  def get_register(self, no):
    return super().get_register(no)
  
  def set_register(self, no, value):
    return super().set_register(no, value)

  def get_pos(self):
    return self._microsteps_to_mm(super().get_xactual())

  def get_latch_pos(self):
    return self._microsteps_to_mm(super().get_xlatch())

  def get_encoder_position(self):
    return self._microsteps_to_mm(super().get_x_enc())

  def get_velocity(self):
    return self._microsteps_to_mm(super().get_vactual())  

  def jog(self, direction, amount=None):
    if amount == None:
        amount = self.jog_amount_def
    if direction == '+':
        amount = abs(amount)
    else:
        amount = -abs(amount)
    amount = self._mm_to_microsteps(amount)
    velocity_max = self._mm_to_microsteps(self.jog_speed)
    super().move_by(amount, velocity_max)

  def position(self, position):
    if position < self.top_pos:
      position = self.top_pos
    if position > self.bottom_pos:
      position = self.bottom_pos
    position = self._mm_to_microsteps(position)
    velocity = self._mm_to_microsteps(self.vmax)
    super().move_to(position, velocity)

  def volume(self, volume):
    volume_distance = self._volume_to_distance(volume)
    position = self.bottom_pos - volume_distance
    if position < self.top_pos:
        position = self.top_pos
    if position >= self.bottom_pos:
        position = self.bottom_pos
    position = self._mm_to_microsteps(position)
    velocity = self._mm_to_microsteps(self.vmax)
    super().move_to(position, velocity)

  def _volume_to_distance(self, volume):
    # convert volume to distance in mm
    volume_distance = volume / (math.pi * self.disk_radius * self.disk_radius)
    return volume_distance

  def pumping(self, action, volume):
    print(f'syringe.pumping({action}, {volume})')
    # calculate volume position
    volume_distance = self._volume_to_distance(volume)
    print(f'syringe.pumping, volume_distance={volume_distance}')
    print(f'syringe.pumping, bottom_pos={self.bottom_pos}')
    position = self.bottom_pos - volume_distance
    if position < self.top_pos:
        position = self.top_pos
    print(f'syringe.pumping, position={position}')
    position = self._mm_to_microsteps(position)
    # set velocity
    velocity = self._mm_to_microsteps(self.slow_pumping_speed)
    if action == 'sup' or action == 'sdown':
      velocity = self._mm_to_microsteps(self.slow_pumping_speed)
    elif action == 'up' or action == 'down':
      velocity = self._mm_to_microsteps(self.pumping_speed)
    # start pumping
    super().move_to(position, velocity)

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
    print('syringe.release_switch()')
    print('checking switch')
    # return if not switch on
    super().unswap_switch()
    super().set_left_switch_active_low()
    if not super().is_switch_on():
      print('switch is not on')
      return
    # set condition to detect switch rising edge (high active)
    print('set switch mode')
    super().swap_switch()
    super().set_right_switch_active_high()
    super().enable_right_switch()
    # move to (+) inf position
    print('moving to + inf')
    position = tmc5130.MAX_POSITION
    # print('moving to - inf')
    # position = tmc5130.MIN_POSITION
    velocity = self._mm_to_microsteps(self.release_switch_speed)
    super().move_to(position, velocity)

  def search_switch(self):
    print('syringe.search_switch()')
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
    velocity = self._mm_to_microsteps(self.search_switch_speed)
    super().move_to(position, velocity)

  def go_to_switch_latch_position(self):
    print('syringe.go_to_switch_latch_position()')
    print(self.get_pos(), self.get_latch_pos())
    position = super().get_xlatch()
    velocity = self._mm_to_microsteps(self.go_to_switch_latch_position_speed)
    super().move_to(position, velocity)

  def search_encoder_n_signal(self):
    # enable driver position latch on encoder n signal
    # clr_cont = 1, is neccessary for latching deiver position
    super().set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)
    # move by one revolution
    distance = self._mm_to_microsteps(self.search_encoder_n_signal_distance)
    velocity = self._mm_to_microsteps(self.search_encoder_n_signal_speed)
    super().move_by(distance, velocity)

  def go_to_encoder_n_signal(self):
    # diable driver position latch on encoder n signal
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)
    # move to latched driver position
    xlatch = super().get_xlatch()
    velocity = self._mm_to_microsteps(self.go_back_to_encoder_n_signal_speed)
    super().move_to(xlatch, velocity)

  def set_home_position(self):
    position = self._mm_to_microsteps(self.home_position)
    self.set_register(tmc5130.XACTUAL, position)
    self.set_register(tmc5130.XTARGET, position)
    self.set_register(tmc5130.X_ENC, position)

  def shift_from_home(self):
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_ENC_X)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    distance = self._mm_to_microsteps(self.shift_from_home_distance)
    velocity = self._mm_to_microsteps(self.shift_from_home_speed)
    super().move_by(distance, velocity)

  # called at the end of home sequence
  def finish_home(self):
    self._reset_switch_mode()
    self._reset_encoder_mode()

  # called by user stop
  def stop_home(self):
    self._reset_switch_mode()
    self._reset_encoder_mode()

  def _reset_switch_mode(self):
    super().set_register(tmc5130.SW_MODE, 0)
    super().enable_soft_switch_stop()
    super().unswap_switch()
    super().set_right_switch_active_low() # right switch is floating
    super().set_left_switch_active_low() # left switch is connected to a low active switch
    super().enable_left_switch()
    super().disable_right_switch()
    super().clear_switch_latches()

  def _reset_encoder_mode(self):
    # diable driver position latch on encoder n signal
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)


  ###################################
  # bottom position
  ###################################
  def save_bottom_position(self):
    try:
      file_name = "./syringe_bottom_pos.txt"
      with open(file_name, "w") as f:
        bottom_pos = self.get_pos()
        f.write(f'{bottom_pos}')
        self.bottom_pos = bottom_pos
        print(f'save_bottom_pos, {bottom_pos}')
    except IOError:
      print('syringe bottom position save failed')

  def _load_bottom_position(self):
    try:
      file_name = "./syringe_bottom_pos.txt"
      with open(file_name, "r") as f:
        pos = f.readline()
        self.bottom_pos = float(pos)
        print(f'_load_bottom_pos, {self.bottom_pos}')
    except IOError:
      print('syringe bottom position load failed')
      self.bottom_pos = self.bottom_pos_def
      print(f'syringe bottom position set with default value {self.bottom_pos}')


  ###################################
  # uint conversion
  ###################################
  def _mm_to_microsteps(self, mm):
    return int(mm * self.microstepes_per_rev / self.lead)
  
  def _microsteps_to_mm(self, microsteps):
    return microsteps * self.lead / self.microstepes_per_rev


#syringe.py
