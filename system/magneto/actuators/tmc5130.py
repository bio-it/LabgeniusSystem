# -*- coding: utf-8 -*-
###############################################################################
# tmc5130.py
###############################################################################
###################################
# constants
###################################
TMC5130_REGISTER_COUNT   = 128
TMC5130_MOTORS           = 1
WRITE_BIT         = 0x80
ADDRESS_MASK      = 0x7f
MAX_VELOCITY      = 8388096
MAX_ACCELERATION  = 65535
MAX_POSITION      = int((pow(2,31)-1)*99/100)
#-int(pow(2,31)-1) not working in move_to
MIN_POSITION      = -int((pow(2,31)-1)*99/100)

###################################
# register and bit size definition
###################################
# register set
# REG_GCONF       = 0x00
# REG_GSTAT       = 0x01
# REG_IFCNT       = 0x02
# REG_SLAVECONF   = 0x03
# REG_IOIN        = 0x04
# REG_X_COMPARE   = 0x05
# REG_IHOLD_IRUN  = 0x10
# REG_TPOWERDOWN  = 0x11
# REG_TSTEP       = 0x12
# REG_TPWMTHRS    = 0x13
# REG_TCOOLTHRS   = 0x14
# REG_THIGH       = 0x15
# REG_RAMPMODE    = 0x20
# REG_XACTUAL     = 0x21
# REG_VACTUAL     = 0x22
# REG_VSTART      = 0x23
# REG_A1          = 0x24
# REG_V1          = 0x25
# REG_AMAX        = 0x26
# REG_VMAX        = 0x27
# REG_DMAX        = 0x28
# REG_D1          = 0x2A
# REG_VSTOP       = 0x2B
# REG_TZEROWAIT   = 0x2C
# REG_XTARGET     = 0x2D
# REG_VDCMIN      = 0x33
# REG_SW_MODE     = 0x34
# REG_RAMP_STAT   = 0x35
# REG_XLATCH      = 0x36
# REG_ENCMODE     = 0x38
# REG_X_ENC       = 0x39
# REG_ENC_CONST   = 0x3A
# REG_ENC_STATUS  = 0x3B
# REG_ENC_LATCH   = 0x3C
# REG_MSLUT0      = 0x60
# REG_MSLUT1      = 0x61
# REG_MSLUT2      = 0x62
# REG_MSLUT3      = 0x63
# REG_MSLUT4      = 0x64
# REG_MSLUT5      = 0x65
# REG_MSLUT6      = 0x66
# REG_MSLUT7      = 0x67
# REG_MSLUTSEL    = 0x68
# REG_MSLUTSTART  = 0x69
# REG_MSCNT       = 0x6A
# REG_MSCURACT    = 0x6B
# REG_CHOPCONF    = 0x6C
# REG_COOLCONF    = 0x6D
# REG_DCCTRL      = 0x6E
# REG_DRVSTATUS   = 0x6F
# REG_PWMCONF     = 0x70
# REG_PWMSTATUS   = 0x71
# REG_ENCM_CTRL   = 0x72
# REG_LOST_STEPS  = 0x73
GCONF = 0x00
GSTAT = 0x01
IFCNT = 0x02
SLAVECONF = 0x03
IOIN = 0x04
X_COMPARE = 0x05
IHOLD_IRUN = 0x10
TPOWERDOWN = 0x11
TSTEP = 0x12
TPWMTHRS = 0x13
TCOOLTHRS = 0x14
THIGH = 0x15
RAMPMODE = 0x20
XACTUAL = 0x21
VACTUAL = 0x22
VSTART = 0x23
A1 = 0x24
V1 = 0x25
AMAX = 0x26
VMAX = 0x27
DMAX = 0x28
D1 = 0x2A
VSTOP = 0x2B
TZEROWAIT = 0x2C
XTARGET = 0x2D
VDCMIN = 0x33
SW_MODE = 0x34
RAMP_STAT = 0x35
XLATCH = 0x36
ENCMODE = 0x38
X_ENC = 0x39
ENC_CONST = 0x3A
ENC_STATUS = 0x3B
ENC_LATCH = 0x3C
MSLUT0 = 0x60
MSLUT1 = 0x61
MSLUT2 = 0x62
MSLUT3 = 0x63
MSLUT4 = 0x64
MSLUT5 = 0x65
MSLUT6 = 0x66
MSLUT7 = 0x67
MSLUTSEL = 0x68
MSLUTSTART = 0x69
MSCNT = 0x6A
MSCURACT = 0x6B
CHOPCONF = 0x6C
COOLCONF = 0x6D
DCCTRL = 0x6E
DRVSTATUS = 0x6F
PWMCONF = 0x70
PWM_SCALE = 0x71
ENCM_CTRL = 0x72
LOST_STEPS = 0x73

###################################
# register template
###################################
class Register(object):
  def __init__(self, name, no, value, readable, writable):
    self.name = name
    self.no = no
    self.value = value
    self.readable = readable
    self.writable = writable

  def __str__(self):
    return f'Register: {self.name}, {self.no}, {self.value}, {self.readable}, {self.writable}'


###################################
# register definition
###################################
_registers = [
  Register('gconf', GCONF, 0, True, True),
  Register('gstat', GSTAT, 0, True, False),
  Register('ifcnt', IFCNT, 0, True, False),
  Register('slaveconf', SLAVECONF, 0, False, True),
  Register('ioin', IOIN, 0, True, False),
  Register('x_comapre', X_COMPARE, 0, False, True),
  Register('ihold_irun', IHOLD_IRUN, 0, False, True),
  Register('tpowerdown', TPOWERDOWN, 0, False, True),
  Register('tstep', TSTEP, 0, True, False),
  Register('tpwmthrs', TPWMTHRS, 0, False, True),
  Register('tcoolthrrs', TCOOLTHRS, 0, False, True),
  Register('thigh', THIGH, 0, False, True),
  Register('rampmode', RAMPMODE, 0, True, True),
  Register('xactual', XACTUAL, 0, True, True),
  Register('vactual', VACTUAL, 0, True, False),
  Register('vstart', VSTART, 0, False, True),
  Register('a1', A1, 0, False, True),
  Register('v1', V1, 0, False, True),
  Register('amax', AMAX, 0, False, True),
  Register('vmax', VMAX, 0, False, True),
  Register('dmax', DMAX, 0, False, True),
  Register('vstop', VSTOP, 0, False, True),
  Register('tzerowait', TZEROWAIT, 0, True, True),
  Register('xtarget', XTARGET, 0, True, True),
  Register('vdcmin', VDCMIN, 0, False, True),
  Register('sw_mode', SW_MODE, 0, True, True),
  Register('ramp_stat', RAMP_STAT, 0, True, False),
  Register('xlatch', XLATCH, 0, True, False),
  Register('encmode', ENCMODE, 0, True, True),
  Register('x_enc', X_ENC, 0, True, True),
  Register('enc_const', ENC_CONST, 0, False, True),
  Register('enc_status', ENC_STATUS, 0, True, False),
  Register('enc_latch', ENC_LATCH, 0, True, False),
  Register('mslut0', MSLUT0, 0, False, True),
  Register('mslut1', MSLUT1, 0, False, True),
  Register('mslut2', MSLUT2, 0, False, True),
  Register('mslut3', MSLUT3, 0, False, True),
  Register('mslut4', MSLUT4, 0, False, True),
  Register('mslut5', MSLUT5, 0, False, True),
  Register('mslut6', MSLUT6, 0, False, True),
  Register('mslut7', MSLUT7, 0, False, True),
  Register('mslutsel', MSLUTSEL, 0, False, True),
  Register('mslutstart', MSLUTSTART, 0, False, True),
  Register('mscnt', MSCNT, 0, True, False),
  Register('mscuract', MSCURACT, 0, True, False),
  Register('chopconf', CHOPCONF, 0, False, True),
  Register('coolconf', COOLCONF, 0, False, True),
  Register('dcctrl', DCCTRL, 0, False, True),
  Register('drvstatus', DRVSTATUS, 0, True, False),
  Register('pwmconf', PWMCONF, 0, False, True),
  Register('pwm_scale', PWM_SCALE, 0, True, False),
  Register('encm_ctrl', ENCM_CTRL, 0, False, True),
  Register('lost_steps', LOST_STEPS, 0, True, False)
]
# dict map with list comprehension
_registers_no_map = {r.no: r for r in _registers}
# dict map with list comprehension
_registers_name_map = {r.name: r for r in _registers}

def is_readable(no):
  register = _registers_no_map[no]
  return register.readable

def is_writable(no):
  register = _registers_no_map[no]
  return register.writable

def name_to_no(name):
  if name in _registers_name_map.keys():
    register = _registers_name_map[name]
    return register.no
  else:
    print(f'tmc5130.name_to_no({name}), no register.')
    return None

# # register access permissions:
# #   0x00: none (reserved)
# #   0x01: read
# #   0x02: write
# #   0x03: read/write
# #   0x13: read/write, seperate functions/values for reading or writing
# #   0x21: read, flag register (read to clear)
# #   0x42: write, has hardware presets on reset
# default_register_accesses = [
# #  0     1     2     3     4     5     6     7     8     9     A     B     C     D     E     F
# 	0x03, 0x21, 0x01, 0x02, 0x13, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 0x00 - 0x0F
# 	0x02, 0x02, 0x01, 0x02, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 0x10 - 0x1F
# 	0x03, 0x03, 0x01, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x00, 0x02, 0x02, 0x02, 0x03, 0x00, 0x00, # 0x20 - 0x2F
# 	0x00, 0x00, 0x00, 0x02, 0x03, 0x21, 0x01, 0x00, 0x03, 0x03, 0x02, 0x21, 0x01, 0x00, 0x00, 0x00, # 0x30 - 0x3F
# 	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 0x40 - 0x4F
# 	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 0x50 - 0x5F
# 	0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x01, 0x01, 0x03, 0x02, 0x02, 0x01, # 0x60 - 0x6F
# 	0x42, 0x01, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  # 0x70 - 0x7F
# ]
'''
// Register access bits
/* Lower nibble is used for read/write, higher nibble is used for
 * special case registers. This makes it easy to identify the read/write
 * part of the permissions in a hexadecimal permission number.
 * The dirty bit will only ever be set at runtime, so we keep the easily
 * readable lower nibble.
 */
'''
# ACCESS_NONE = 0x00
# ACCESS_READ = 0x01
# ACCESS_WRITE= 0x02
# ACCESS_DIRTY= 0x08 # written since reset -> shadow register is valid for restore
# ACCESS_RW_SPECIAL = 0x10 # read and write are independent - different values and/or different functions
# ACCESS_FLAGS      = 0x20 # register has read or write to clear flags.
# ACCESS_HW_PRESET  = 0x40 # has hardware presets (e.g. Factory calibrations) - do not write a default value
# ACCESS_RW         = (ACCESS_READ  | ACCESS_WRITE)     # 0x03 - Read and write
# ACCESS_RW_SEPARATE= (ACCESS_RW    | ACCESS_RW_SPECIAL)# 0x13 - Read and write, with separate values/functions
# ACCESS_R_FLAGS    = (ACCESS_READ  | ACCESS_FLAGS)     # 0x21 - Read, has flags (read to clear)
# ACCESS_RW_FLAGS   = (ACCESS_RW    | ACCESS_FLAGS)     # 0x23 - Read and write, has flags (read or write to clear)
# ACCESS_W_PRESET   = (ACCESS_WRITE | ACCESS_HW_PRESET) # 0x42 - Write, has hardware preset - skipped in reset routine
# ACCESS_RW_PRESET  = (ACCESS_RW    | ACCESS_HW_PRESET) # 0x43 - Read and write, has hardware presets - skipped in reset routine
# def is_access_readable(access):
#   return True if (access & ACCESS_READ) != 0 else False
# def is_access_writable(access):
#   return True if (access & ACCESS_WRITE) != 0 else False
# def is_access_dirty(access):
#   return True if (access & ACCESS_DIRTY) != 0 else False
# #define TMC_IS_RESETTABLE(x)  (((x) & (TMC_ACCESS_W_PRESET)) == TMC_ACCESS_WRITE) // Write bit set, Hardware preset bit not set
# #define TMC_IS_RESTORABLE(x)  (((x) & TMC_ACCESS_WRITE) && (!(x & TMC_ACCESS_HW_PRESET) || (x & TMC_ACCESS_DIRTY))) // Write bit set, if it's a hardware preset register, it needs to be dirty


# R10 = 0x00071703  # IHOLD_IRUN
# R3A = 0x00010000  # ENC_CONST
# R6C = 0x000101D5  # CHOPCONF
# reset_register_values = [
# #	0,   1,   2,   3,   4,   5,   6,   7,   8,   9,   A,   B,   C,   D,   E,   F
# 	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x00 - 0x0F
# 	R10, 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x10 - 0x1F
# 	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x20 - 0x2F
# 	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   R3A, 0,   0,   0,   0,   0, # 0x30 - 0x3F
# 	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x40 - 0x4F
# 	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x50 - 0x5F
# 	None,None,None,None,None,None,None,None,None,None, 0,   0,  R6C, 0,   0,   0, # 0x60 - 0x6F
# 	None,0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, # 0x70 - 0x7F
# ]

# global configuration (register GCONF)
BIT_GCONF_EN_PWM_MODE = 0x0004
BIT_GCONF_SHAFT = 0x0010 # inverse motor direction

# ramp modes (register RAMPMODE)
RAMPMODE_POSITION  = 0
RAMPMODE_VELPOS    = 1
RAMPMODE_VELNEG    = 2
RAMPMODE_HOLD      = 3
# limit switch mode bits (register SWMODE)
BIT_SW_MODE_STOP_L_ENABLE    = 0x0001
BIT_SW_MODE_STOP_R_ENABLE    = 0x0002
BIT_SW_MODE_POL_STOP_L       = 0x0004
BIT_SW_MODE_POL_STOP_R       = 0x0008
BIT_SW_MODE_SWAP_LR          = 0x0010
BIT_SW_MODE_LATCH_L_ACTIVE   = 0x0020
BIT_SW_MODE_LATCH_L_INACTIVE = 0x0040
BIT_SW_MODE_LATCH_R_ACTIVE   = 0x0080
BIT_SW_MODE_LATCH_R_INACTIVE = 0x0100
BIT_SW_MODE_EN_LATCH_ENCODER = 0x0200
BIT_SW_MODE_SG_STOP          = 0x0400
BIT_SW_MODE_EN_SOFTSTOP      = 0x0800
def get_sw_mode_string(sw_mode):
  string = ''
  if sw_mode & BIT_SW_MODE_STOP_L_ENABLE: string += 'stop_l_enable '
  if sw_mode & BIT_SW_MODE_STOP_R_ENABLE: string += 'stop_r_enable '
  if sw_mode & BIT_SW_MODE_POL_STOP_L: string += 'pol_stop_l '
  if sw_mode & BIT_SW_MODE_POL_STOP_R: string += 'pol_stop_r '
  if sw_mode & BIT_SW_MODE_SWAP_LR: string += 'swap_lr '
  if sw_mode & BIT_SW_MODE_LATCH_L_ACTIVE: string += 'latch_l_active '
  if sw_mode & BIT_SW_MODE_LATCH_L_INACTIVE: string += 'latch_l_inactive '
  if sw_mode & BIT_SW_MODE_LATCH_R_ACTIVE: string += 'latch_r_active '
  if sw_mode & BIT_SW_MODE_LATCH_R_INACTIVE: string += 'latch_r_inactive '
  if sw_mode & BIT_SW_MODE_EN_LATCH_ENCODER: string += 'en_latch_encoder '
  if sw_mode & BIT_SW_MODE_SG_STOP: string += 'sg_stop '
  if sw_mode & BIT_SW_MODE_EN_SOFTSTOP: string += 'en_softstop '
  return string

# ramp status bits (register RAMPSTAT)
BIT_RAMP_STAT_STOP_L            = 0x0001
BIT_RAMP_STAT_STOP_R            = 0x0002
BIT_RAMP_STAT_LATCH_L           = 0x0004
BIT_RAMP_STAT_LATCH_R           = 0x0008
BIT_RAMP_STAT_EV_STOP_L         = 0x0010
BIT_RAMP_STAT_EV_STOP_R         = 0x0020
BIT_RAMP_STAT_EV_STOP_SG        = 0x0040
BIT_RAMP_STAT_EV_POS_REACHED    = 0x0080
BIT_RAMP_STAT_VELOCITY_REACHED  = 0x0100
BIT_RAMP_STAT_POSITION_REACHED  = 0x0200
BIT_RAMP_STAT_VZERO             = 0x0400
BIT_RAMP_STAT_T_ZEROWAIT_ACTIVE = 0x0800
BIT_RAMP_STAT_SECOND_MOVE       = 0x1000
BIT_RAMP_STAT_SG                = 0x2000
def get_ramp_stat_string(ramp_stat):
  string = ''
  if ramp_stat & BIT_RAMP_STAT_STOP_L: string += 'stop_l '
  if ramp_stat & BIT_RAMP_STAT_STOP_R: string += 'stop_r '
  if ramp_stat & BIT_RAMP_STAT_LATCH_L: string += 'latch_l '
  if ramp_stat & BIT_RAMP_STAT_LATCH_R: string += 'latch_r '
  if ramp_stat & BIT_RAMP_STAT_EV_STOP_L: string += 'event_stop_l '
  if ramp_stat & BIT_RAMP_STAT_EV_STOP_R: string += 'event_stop_r '
  if ramp_stat & BIT_RAMP_STAT_EV_STOP_SG: string += 'event_stop_sg '
  if ramp_stat & BIT_RAMP_STAT_EV_POS_REACHED: string += 'event_pos_reached '
  if ramp_stat & BIT_RAMP_STAT_VELOCITY_REACHED: string += 'event_velocity_reached '
  if ramp_stat & BIT_RAMP_STAT_POSITION_REACHED: string += 'position_reached '
  if ramp_stat & BIT_RAMP_STAT_VZERO: string += 'vzero '
  if ramp_stat & BIT_RAMP_STAT_T_ZEROWAIT_ACTIVE: string += 't_zero_wait_active '
  if ramp_stat & BIT_RAMP_STAT_SECOND_MOVE: string += 'second_move '
  if ramp_stat & BIT_RAMP_STAT_SG: string += 'status_sg '
  return string

RAMP_STAT_STATUS_STOP_L_MASK  = 0x01; RAMP_STAT_STATUS_STOP_L_SHIFT = 0
RAMP_STAT_STATUS_STOP_R_MASK  = 0x02; RAMP_STAT_STATUS_STOP_R_SHIFT = 1
RAMP_STAT_STATUS_LATCH_L_MASK = 0x04; RAMP_STAT_STATUS_LATCH_L_SHIFT  = 2
RAMP_STAT_STATUS_LATCH_R_MASK   = 0x08; RAMP_STAT_STATUS_LATCH_R_SHIFT  = 3
RAMP_STAT_EVENT_STOP_L_MASK     = 0x10; RAMP_STAT_EVENT_STOP_L_SHIFT    = 4
RAMP_STAT_EVENT_STOP_R_MASK     = 0x20; RAMP_STAT_EVENT_STOP_R_SHIFT    = 5
RAMP_STAT_EVENT_STOP_SG_MASK    = 0x40; RAMP_STAT_EVENT_STOP_SG_SHIFT   = 6
RAMP_STAT_EVENT_POS_REACHED_MASK  = 0x80; RAMP_STAT_EVENT_POS_REACHED_SHIFT = 7
RAMP_STAT_VELOCITY_REACHED_MASK   = 0x0100; RAMP_STAT_VELOCITY_REACHED_SHIFT  = 8
RAMP_STAT_POSITION_REACHED_MASK   = 0x0200; RAMP_STAT_POSITION_REACHED_SHIFT  = 9
RAMP_STAT_VZERO_MASK              = 0x0400; RAMP_STAT_VZERO_SHIFT             = 10
RAMP_STAT_T_ZEROWAIT_ACTIVE_MASK  = 0x0800; RAMP_STAT_T_ZEROWAIT_ACTIVE_SHIFT = 11
RAMP_STAT_SECOND_MOVE_MASK        = 0x1000; RAMP_STAT_SECOND_MOVE_SHIFT       = 12
RAMP_STAT_STATUS_SG_MASK          = 0x2000; RAMP_STAT_STATUS_SG_SHIFT         = 13

BIT_ENC_STATUS_N_EVENT  = 0x01

BIT_ENCMODE_ENC_SEL_DECIMAL = 0x0400
BIT_ENCMODE_LATCH_X_ACT     = 0x0200
BIT_ENCMODE_CLR_ENC_X       = 0x0100
BIT_ENCMODE_NEG_EDGE        = 0x0080
BIT_ENCMODE_POS_EDGE        = 0x0040
BIT_ENCMODE_CLR_ONCE        = 0x0020
BIT_ENCMODE_CLR_CONT        = 0x0010
BIT_ENCMODE_IGNORE_AB       = 0x0008
BIT_ENCMODE_POL_N           = 0x0004
BIT_ENCMODE_POL_B           = 0x0002
BIT_ENCMODE_POL_A           = 0x0001
ENCMODE_N_EDGE_MASK  = 0x00c0; ENCMODE_N_EDGE_SHIFT = 6
ENCMODE_N_EDGE_LEVEL  = 0
ENCMODE_N_EDGE_RISING = 1
ENCMODE_N_EDGE_FALLING= 2
ENCMODE_N_EDGE_BOTH   = 3

IHOLD_MASK       = 0x0000001f; IHOLD_SHIFT = 0
IRUN_MASK        = 0x00001f00; IRUN_SHIFT = 8
IHOLDDELAY_MASK  = 0x000f0000; IHOLDDELAY_SHIFT = 16
IHOLD_MAX = 31
IRUN_MAX = 31
IHOLDDELAY_MAX = 31

#tmc5130.py
