# -*- coding: utf-8 -*-
###############################################################################
# tmc5130_stepper.py
###############################################################################
import magneto.actuators.tmc5130 as tmc5130


###############################################################################
# TMC5130 stepper driver class
###############################################################################
class TMC5130Stepper():
  ###################################
  # __init__
  ###################################
  def __init__(self, spi):
    self.spi = spi
    self.f_clk = 1.27574e+07
    self.vel_t = pow(2, 24) / self.f_clk  # [s/clk]
    self.acc_ta2 = pow(2, 41) / self.f_clk / self.f_clk  # [s^2/clk^2]
    # self.register_access_states = [
    #     access for access in tmc5130.default_register_accesses]
    # self.register_values = [value for value in tmc5130.reset_register_values]
    self.shadow_register_values = {r.no:r.value for r in tmc5130._registers}
    # print(self.shadow_register_values)

  ###################################
  # set/get register
  ###################################
  def get_registers(self):
    registers = {r.name: r.value for r in tmc5130._registers}
    for name in registers.keys():
      no = tmc5130.name_to_no(name)
      value = self.get_register(no)
      registers[name] = value
    return registers

  def set_register(self, address, value):
    value = int(value)
    write_buf = bytearray(5)
    write_buf[0] = address | tmc5130.WRITE_BIT
    write_buf[1] = (value >> 24) & 0xff
    write_buf[2] = (value >> 16) & 0xff
    write_buf[3] = (value >> 8) & 0xff
    write_buf[4] = (value >> 0) & 0xff
    self.spi.xfer(write_buf)
    self.shadow_register_values[address] = value

  def get_register(self, address):
    address = address & tmc5130.ADDRESS_MASK
    # access = self.register_access_states[address]
    # if not tmc5130.is_readable(access):
    if not tmc5130.is_readable(address):
      return self.shadow_register_values[address]
    write_buf = bytearray(5)
    write_buf[0] = address
    read_buf = self.spi.xfer(write_buf)
    read_buf = self.spi.xfer(write_buf)
    return int.from_bytes(read_buf[1:], byteorder='big', signed=False)

  def set_register_bit(self, no, bit):
    value = self.get_register(no)
    value = value | bit
    self.set_register(no, value)

  def clear_register_bit(self, no, bit):
    value = self.get_register(no)
    value = value & ~bit
    self.set_register(no, value)

  def get_register_field(self, no, mask, shift):
    return (self.get_register(no) & mask) >> shift

  def set_register_field(self, no, mask, shift, value):
    data = self.get_register(no)
    data = (data & ~mask) | ((value << shift) & mask)
    self.set_register(no, data)

  ###################################
  # motion commands
  ###################################
  def move_to(self, position, velocity_max):
    self.set_register(tmc5130.RAMPMODE, tmc5130.RAMPMODE_POSITION)
    self.set_vmax(velocity_max)
    self.set_register(tmc5130.XTARGET, position)

  def move_by(self, delta, velocity_max):
    position = delta + self.get_register(tmc5130.XACTUAL)
    self.move_to(position, velocity_max)

  # def rotate(self, velocity):
  #   self.set_register(tmc5130.VMAX, abs(velocity))
  #   if velocity >= 0:
  #     ramp_mode = tmc5130.RAMPMODE_VELPOS
  #   else:
  #     ramp_mode = tmc5130.RAMPMODE_VELNEG
  #   self.set_register(tmc5130.RAMPMODE, ramp_mode)

  # def right(self, velocity):
  #   self.rotoate(velocity)

  # def left(self, velocity):
  #   self.rotoate(-velocity)

  ###################################
  # home commands
  ###################################

  ###################################
  # reset, stop
  ###################################
  def stop(self, velocity=0):
    self.set_register(tmc5130.RAMPMODE, tmc5130.RAMPMODE_VELPOS)
    self.set_register(tmc5130.VMAX, 0)
    xactual = self.get_register(tmc5130.XACTUAL)
    self.set_register(tmc5130.XTARGET, xactual)
    self.clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_ONCE)
    self.clear_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_CLR_ENC_X)

  ###################################
  # status
  ###################################
  def has_n_event(self):
    return self.get_register(tmc5130.ENC_STATUS) & tmc5130.BIT_ENC_STATUS_N_EVENT

  def is_busy(self):
    # return not self.get_register(tmc5130.RAMP_STAT) & tmc5130.BIT_RAMP_STAT_POSITION_REACHED
    return not (self.get_register(tmc5130.RAMP_STAT) & tmc5130.BIT_RAMP_STAT_VZERO)

  ###################################
  # switch mode
  # left switch is connected to sensor
  # right switch is floating
  ###################################
  def is_switch_swapped(self):
    return self.get_register(tmc5130.SW_MODE) & tmc5130.BIT_SW_MODE_SWAP_LR

  def unswap_switch(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_SWAP_LR)

  def swap_switch(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_SWAP_LR)

  def is_switch_on(self):
    if self.is_switch_swapped():
      return self.get_register(tmc5130.RAMP_STAT) & tmc5130.BIT_RAMP_STAT_STOP_R
    else:
      return self.get_register(tmc5130.RAMP_STAT) & tmc5130.BIT_RAMP_STAT_STOP_L

  def set_left_switch_active_low(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_L)

  def set_left_switch_active_high(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_L)

  def set_right_switch_active_low(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_R)

  def set_right_switch_active_high(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_POL_STOP_R)

  def enable_left_switch(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_STOP_L_ENABLE)

  def disable_left_switch(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_STOP_L_ENABLE)

  def enable_right_switch(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_STOP_R_ENABLE)

  def disable_right_switch(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_STOP_R_ENABLE)

  def set_left_switch_latch_active(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_LATCH_L_ACTIVE)
  
  def clear_switch_latches(self):
    self.clear_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_LATCH_L_ACTIVE)

  def enable_soft_switch_stop(self):
    self.set_register_bit(tmc5130.SW_MODE, tmc5130.BIT_SW_MODE_EN_SOFTSTOP)


  ###################################
  # encoder mode
  ###################################
  def set_encoder_n_signal_high_active(self):
    self.set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_POL_N)
  def ignore_ab_for_encoder_n_signal(self):
    self.set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_IGNORE_AB)
  def set_encoder_n_signal_event_rising_edge(self):
    self.set_register_field(tmc5130.ENCMODE, tmc5130.ENCMODE_N_EDGE_MASK, tmc5130.ENCMODE_N_EDGE_SHIFT, tmc5130.ENCMODE_N_EDGE_RISING)
  def set_encoder_select_decimal(self):
    self.set_register_bit(tmc5130.ENCMODE, tmc5130.BIT_ENCMODE_ENC_SEL_DECIMAL)

  ###################################
  # speed profile
  ###################################
  def set_vstart(self, vstart):
    self.set_register(tmc5130.VSTART, vstart)

  def set_a1(self, a1):
    a1 = a1 * self.acc_ta2
    self.set_register(tmc5130.A1, a1)

  def set_v1(self, v1):
    v1 = v1 * self.vel_t
    self.set_register(tmc5130.V1, v1)

  def set_amax(self, amax):
    amax = amax * self.acc_ta2
    self.set_register(tmc5130.AMAX, amax)

  def set_vmax(self, vmax):
    vmax = vmax * self.vel_t
    self.set_register(tmc5130.VMAX, vmax)

  def set_dmax(self, dmax):
    dmax = dmax * self.acc_ta2
    self.set_register(tmc5130.DMAX, dmax)

  def set_d1(self, d1):
    d1 = d1 * self.acc_ta2
    self.set_register(tmc5130.D1, d1)

  def set_vstop(self, vstop):
    self.set_register(tmc5130.VSTOP, vstop)

  def get_xactual(self):
    xactual = self.get_register(tmc5130.XACTUAL)
    if xactual & 0x80000000:
      xactual = xactual | ~((0x01 << 32)-1)
    return xactual

  def get_xlatch(self):
    xlatch = self.get_register(tmc5130.XLATCH)
    if xlatch & 0x80000000:
      xlatch = xlatch | ~((0x01 << 32)-1)
    return xlatch

  def get_vactual(self):
    vactual = self.get_register(tmc5130.VACTUAL)
    if vactual & 0x00800000:
      vactual = vactual | ~((0x01 << 24)-1)
    vactual = vactual / self.vel_t # microsteps/s
    return vactual

  def get_x_enc(self):
    x_enc = self.get_register(tmc5130.X_ENC)
    if x_enc & 0x80000000:
      x_enc = x_enc | ~((0x01 << 32)-1)
    return x_enc


  ###################################
  # etc
  ###################################
  def set_ihold(self, value):
    self.set_register_field(tmc5130.IHOLD_IRUN, \
                            tmc5130.IHOLD_MASK, \
                            tmc5130.IHOLD_SHIFT, value)
  def set_irun(self, value):
    self.set_register_field(tmc5130.IHOLD_IRUN, \
                            tmc5130.IRUN_MASK, \
                            tmc5130.IRUN_SHIFT, value)
  def set_iholddelay(self, value):
    self.set_register_field(tmc5130.IHOLD_IRUN, \
                            tmc5130.IHOLDDELAY_MASK, \
                            tmc5130.IHOLDDELAY_SHIFT, value)


  #class TMC5130Stepper
#tmc5130_stepper.py
