# -*- coding: utf-8 -*-
###############################################################################
# chamber.py
###############################################################################
import magneto.actuators.tmc5130 as tmc5130
from magneto.actuators.tmc5130_stepper import TMC5130Stepper
from time import sleep


class Chamber(TMC5130Stepper):
  ###################################
  # __init__
  ###################################
  def __init__(self, spi):
    print('chamber class')
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
    super().set_register(tmc5130.GCONF, 0x00000004)
    # 1001 0001 0x13 TPWM_THRS
    # SPI send: 0x93000001F4; // TPWM_THRS=500 yields a switching velocity about 35000 = ca. 30RPM
    # super().set_register(tmc5130.TPWMTHRS, 500)
    super().set_register(tmc5130.TPWMTHRS, 2000)
    # 1111 0111 0x70 PWMCONF
    # SPI send: 0xF0000401C8; // PWMCONF: AUTO=1, 2/1024 Fclk, Switch amplitude limit=200, Grad=1
    super().set_register(tmc5130.PWMCONF, 0x000401C8)

    # # GCONF
    # super().set_register(0x00, 0x00000000)
    # # CHOPCONF: TOFF=5, HSTRT=5, HEND=3, TBL=2, CHM=0 (spreadcycle)
    # super().set_register(0x6C, 0x000101D5)
    # # # IHOLD_IRUN: IHOLD=3, IRUN=6 (max.current?), IHOLDDELAY=7
    # # super().set_register(0x10, 0x00070603)
    # super().set_ihold(10) # 3
    # super().set_irun(20) # 10 <- 6
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
    self.vmax = 360.0 * 2 # [rev/s]
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
    self.jog_amount_default = 5  # [deg]
    self.jog_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s

    # position
    super().set_register(tmc5130.RAMPMODE, 0x00000000)  # RAMPMODE=0
    super().set_register(tmc5130.XACTUAL, 0x00000000)  # XACTUAL=0
    super().set_register(tmc5130.XTARGET, 0x00000000)  # XTARGET=0

    # encoder setting
    super().set_register(tmc5130.X_ENC, 0)
    super().set_encoder_n_signal_high_active()
    super().ignore_ab_for_encoder_n_signal()
    super().set_encoder_n_signal_event_rising_edge()
    self._reset_encoder_mode()
    # encoder constant
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
    super().set_encoder_select_decimal()
    super().set_register(tmc5130.ENC_CONST, ((12*(1<<16)) | (5000)))

    # switch mode - no switch

    # homing
    self.search_encoder_n_signal_speed = 360.0 # [deg/s]
    self.search_encoder_n_signal_distance = -370.0 # [deg/s]
    self.go_to_encoder_n_signal_speed = 360.0 # [deg/s]
    self.go_to_offset_position_speed  = 360.0 # [deg/s]
    self.home_position = 0.0 # [deg]
    self.shift_from_home_speed = 360.0 # [deg/s]
    self.shift_from_home_distance = 0.0 # [deg]

    # chamber offset
    self.offset_pos_def = 0.0 # [deg] encoder n signal position
    self.offset_pos = self.offset_pos_def # loaded to and saved from a file
    # self.save_offset_position()
    self.load_offset_position()

    # chamber change
    self.min_chamber_no = 1
    self.max_chamber_no = 13
    self.goto_speed = 360.0 * 2  # [deg/s], 360*2 deg in 2 s


  ###################################
  # interface functions
  ###################################
  def get_register(self, no):
    return super().get_register(no)
  
  def set_register(self, no, value):
    return super().set_register(no, value)

  def get_min_chamber_no(self):
      return self.min_chamber_no

  def get_max_chamber_no(self):
      return self.max_chamber_no

  def get_pos(self):
    return self._microsteps_to_deg(super().get_xactual())

  def get_encoder_position(self):
    return self._microsteps_to_deg(super().get_x_enc())

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
    if no < self.min_chamber_no:
      print(f'goto chamber no {no} is not valid')
      return
    if no > self.max_chamber_no:
      print(f'goto chamber no {no} is not valid')
      return
    position = self.no_to_deggree(no)
    print(f'goto():{position}, {self._deg_to_microsteps(position)}')
    position = self._deg_to_microsteps(position)
    velocity_max = self._deg_to_microsteps(self.goto_speed)
    super().move_to(position, velocity_max)

  def position(self, position):
    position = self._deg_to_microsteps(position)
    velocity = self._deg_to_microsteps(self.vmax)
    super().move_to(position, velocity)

  '''
  mechanical considerations:
  - from top view, (+) direction is CW and (-) direction is CCW
  - from top view
          ======
              13
      12     |    1
  11         |th/eta 2
  10          |/
              --------  3
  9                    
      8               4
          7       5
              6
              ===
  - chamber 6: sample reservoir, with a large hole
  - chamber 13: no physical chamber, connected to chip
  - theta - 20.77 deg
  '''
  def no_to_deggree(self, chamber_no):
    theta = 20.77
    ch_3_pos = 90.0 - theta
    chamber_no_diff = chamber_no - 3
    pos = chamber_no_diff * 360 / 13
    pos = pos + ch_3_pos
    if pos > 360.0:
        pos = pos - 360
    return pos

  def stop(self):
    super().stop()
    self.stop_home()

  def wait(self):
    return super().is_busy()


  ###################################
  # home functions
  ###################################
  def search_encoder_n_signal(self):
    # enable driver position latch on encoder n signal
    # clr_cont = 1, is neccessary for latching deiver position
    super().set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)
    # move by one revolution
    distance = self._deg_to_microsteps(self.search_encoder_n_signal_distance)
    velocity = self._deg_to_microsteps(self.search_encoder_n_signal_speed)
    super().move_by(distance, velocity)

  def go_to_encoder_n_signal(self):
    # diable driver position latch on encoder n signal
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)
    # move to latched driver position
    xlatch = super().get_xlatch()
    velocity = self._deg_to_microsteps(self.go_to_encoder_n_signal_speed)
    super().move_to(xlatch, velocity)

  def go_to_offset_position(self):
    # clear driver and encoder positions
    super().set_register(tmc5130.XACTUAL, 0)
    super().set_register(tmc5130.X_ENC, 0)
    # move to offset position
    position = self._deg_to_microsteps(self.offset_pos)
    velocity = self._deg_to_microsteps(self.go_to_offset_position_speed)
    super().move_to(position, velocity)

  def set_home_position(self):
    position = self._deg_to_microsteps(self.home_position)
    self.set_register(tmc5130.XACTUAL, position)
    self.set_register(tmc5130.XTARGET, position)
    self.set_register(tmc5130.X_ENC, position)

  def shift_from_home(self):
    distance = self._deg_to_microsteps(self.shift_from_home_distance)
    velocity = self._deg_to_microsteps(self.shift_from_home_speed)
    super().move_by(distance, velocity)

  # called at the end of home sequence
  def finish_home(self):
    self._reset_encoder_mode()

  # called by user stop
  def stop_home(self):
    self._reset_encoder_mode()

  def _reset_encoder_mode(self):
    # diable driver position latch on encoder n signal
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_CONT)
    super().clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_LATCH_X_ACT)


  ###################################
  # offset position
  ###################################
  def save_offset_position(self):
    try:
      file_name = "./chamber_offset_position.txt"
      with open(file_name, "w") as f:
        offset_pos = self.get_pos()
        f.write(f'{offset_pos}')
        self.offset_pos = offset_pos
        print(f'save_offset_position, {offset_pos}')
    except IOError:
      print('chamber offset position save failed')

  def load_offset_position(self):
    try:
      file_name = "./chamber_offset_position.txt"
      with open(file_name, "r") as f:
        pos = f.readline()
        self.offset_pos = float(pos)
        # print(f'load_offset_position, {self.offset_pos}')
    except IOError:
      print('chamber offset position load failed')
      self.offset_pos = self.offset_pos_def
      print(f'chamber offset position set with default value {self.offset_pos}')


  ###################################
  # uint conversion
  ###################################
  def _deg_to_microsteps(self, deg):
    return int(deg * self.microstepes_per_rev / 360.0)
  
  def _microsteps_to_deg(self, microsteps):
    return microsteps * 360.0 / self.microstepes_per_rev


#chamber.py
