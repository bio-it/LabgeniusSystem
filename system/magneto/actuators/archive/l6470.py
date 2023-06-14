###################################
# register template
###################################
class Register(object):
    def __init__(self, name, no, bitlen, def_value, value, writable):
        self.name = name
        self.no = no
        self.bitlen = bitlen
        self.def_value = def_value # only for simulator
        self.value = value # only for simulator
        self.writable = writable
    def __str__(self):
        return f'Register: {self.name}, {self.no}, {self.bitlen}, {self.def_value}, {self.writable}'
#class Register

###################################
# register and bit size definition
###################################
ABS_POS    = 0x01; ABS_POS_BITLEN = 22;     ABS_POS_NAME = 'abs_pos';       ABS_POS_DEF = 0
EL_POS     = 0x02; EL_POS_BITLEN = 9;       EL_POS_NAME = 'el_pos';         EL_POS_DEF = 0
MARK       = 0x03; MARK_BITLEN = 22;        MARK_NAME = 'mark';             MARK_DEF = 0
SPEED      = 0x04; SPEED_BITLEN = 20;       SPEED_NAME = 'speed';           SPEED_DEF = 0
ACC        = 0x05; ACC_BITLEN = 12;         ACC_NAME = 'acc';               ACC_DEF = 0x08a
DEC        = 0x06; DEC_BITLEN = 12;         DEC_NAME = 'dec';               DEC_DEF = 0x08a
MAX_SPEED  = 0x07; MAX_SPEED_BITLEN = 10;   MAX_SPEED_NAME = 'max_speed';   MAX_SPEED_DEF = 0x041
MIN_SPEED  = 0x08; MIN_SPEED_BITLEN = 13;   MIN_SPEED_NAME = 'min_speed';   MIN_SPEED_DEF = 0
FS_SPD     = 0x15; FS_SPD_BITLEN = 10;      FS_SPD_NAME = 'fs_spd';         FS_SPD_DEF = 0x027
KVAL_HOLD  = 0x09; KVAL_HOLD_BITLEN = 8;    KVAL_HOLD_NAME = 'kval_hold';   KVAL_HOLD_DEF = 0x29
KVAL_RUN   = 0x0A; KVAL_RUN_BITLEN = 8;     KVAL_RUN_NAME = 'kval_run';     KVAL_RUN_DEF = 0x29
KVAL_ACC   = 0x0B; KVAL_ACC_BITLEN = 8;     KVAL_ACC_NAME = 'kval_acc';     KVAL_ACC_DEF = 0x29
KVAL_DEC   = 0x0C; KVAL_DEC_BITLEN = 8;     KVAL_DEC_NAME = 'kval_dec';     KVAL_DEC_DEF = 0x29
INT_SPD    = 0x0D; INT_SPD_BITLEN = 14;     INT_SPD_NAME = 'int_spd';       INT_SPD_DEF = 0x0408
ST_SLP     = 0x0E; ST_SLP_BITLEN = 8;       ST_SLP_NAME = 'st_slp';         ST_SLP_DEF = 0x19
FN_SLP_ACC = 0x0F; FN_SLP_ACC_BITLEN = 8;   FN_SLP_ACC_NAME = 'fn_slp_acc'; FN_SLP_ACC_DEF = 0x29
FN_SLP_DEC = 0x10; FN_SLP_DEC_BITLEN = 8;   FN_SLP_DEC_NAME = 'fn_slp_dec'; FN_SLP_DEC_DEF = 0x29
K_THERM    = 0x11; K_THERM_BITLEN = 4;      K_THERM_NAME = 'k_therm';       K_THERM_DEF = 0
ADC_OUT    = 0x12; ADC_OUT_BITLEN = 5;      ADC_OUT_NAME = 'adc_out';       ADC_OUT_DEF = 0
OCD_TH     = 0x13; OCD_TH_BITLEN = 4;       OCD_TH_NAME = 'ocd_th';         OCD_TH_DEF = 0x08
STALL_TH   = 0x14; STALL_TH_BITLEN = 7;     STALL_TH_NAME = 'stall_th';     STALL_TH_DEF = 0x40
STEP_MODE  = 0x16; STEP_MODE_BITLEN = 8;    STEP_MODE_NAME = 'step_mode';   STEP_MODE_DEF = 0x07
ALARM_EN   = 0x17; ALARM_EN_BITLEN = 8;     ALARM_EN_NAME = 'alram_en';     ALARM_EN_DEF = 0xff
CONFIG     = 0x18; CONFIG_BITLEN = 16;      CONFIG_NAME = 'config';         CONFIG_DEF = 0x2e88
STATUS     = 0x19; STATUS_BITLEN = 16;      STATUS_NAME = 'status';         STATUS_DEF = 0

###################################
# register functions
###################################
_registers = [
    Register(ABS_POS_NAME, ABS_POS, ABS_POS_BITLEN, ABS_POS_DEF, ABS_POS_DEF, True),
    Register(EL_POS_NAME, EL_POS, EL_POS_BITLEN, EL_POS_DEF, EL_POS_DEF, False),
    Register(MARK_NAME, MARK, MARK_BITLEN, MARK_DEF, MARK_DEF, False),
    Register(SPEED_NAME, SPEED, SPEED_BITLEN, SPEED_DEF, SPEED_DEF, False),
    Register(ACC_NAME, ACC, ACC_BITLEN, ACC_DEF, ACC_DEF, True),
    Register(DEC_NAME, DEC, DEC_BITLEN, DEC_DEF, DEC_DEF, True),
    Register(MAX_SPEED_NAME, MAX_SPEED, MAX_SPEED_BITLEN, MAX_SPEED_DEF, MAX_SPEED_DEF, True),
    Register(MIN_SPEED_NAME, MIN_SPEED, MIN_SPEED_BITLEN, MIN_SPEED_DEF, MIN_SPEED_DEF, True),
    Register(FS_SPD_NAME, FS_SPD, FS_SPD_BITLEN, FS_SPD_DEF, FS_SPD_DEF, True),
    Register(KVAL_HOLD_NAME, KVAL_HOLD, KVAL_HOLD_BITLEN, KVAL_HOLD_DEF, KVAL_HOLD_DEF, True),
    Register(KVAL_RUN_NAME, KVAL_RUN, KVAL_RUN_BITLEN, KVAL_RUN_DEF, KVAL_RUN_DEF, True),
    Register(KVAL_ACC_NAME, KVAL_ACC, KVAL_ACC_BITLEN, KVAL_ACC_DEF, KVAL_ACC_DEF, True),
    Register(KVAL_DEC_NAME, KVAL_DEC, KVAL_DEC_BITLEN, KVAL_DEC_DEF, KVAL_DEC_DEF, True),
    Register(INT_SPD_NAME, INT_SPD, INT_SPD_BITLEN, INT_SPD_DEF, INT_SPD_DEF, True),
    Register(ST_SLP_NAME, ST_SLP, ST_SLP_BITLEN, ST_SLP_DEF, ST_SLP_DEF, True),
    Register(FN_SLP_ACC_NAME, FN_SLP_ACC, FN_SLP_ACC_BITLEN, FN_SLP_ACC_DEF, FN_SLP_ACC_DEF, True),
    Register(FN_SLP_DEC_NAME, FN_SLP_DEC, FN_SLP_DEC_BITLEN, FN_SLP_DEC_DEF, FN_SLP_DEC_DEF, True),
    Register(K_THERM_NAME, K_THERM, K_THERM_BITLEN, K_THERM_DEF, K_THERM_DEF, True),
    Register(ADC_OUT_NAME, ADC_OUT, ADC_OUT_BITLEN, ADC_OUT_DEF, ADC_OUT_DEF, False),
    Register(OCD_TH_NAME, OCD_TH, OCD_TH_BITLEN, OCD_TH_DEF, OCD_TH_DEF, True),
    Register(STALL_TH_NAME, STALL_TH, STALL_TH_BITLEN, STALL_TH_DEF, STALL_TH_DEF, True),
    Register(STEP_MODE_NAME, STEP_MODE, STEP_MODE_BITLEN, STEP_MODE_DEF, STEP_MODE_DEF, True),
    Register(ALARM_EN_NAME, ALARM_EN, ALARM_EN_BITLEN, ALARM_EN_DEF, ALARM_EN_DEF, True),
    Register(CONFIG_NAME, CONFIG, CONFIG_BITLEN, CONFIG_DEF, CONFIG_DEF, True),
    Register(STATUS_NAME, STATUS, STATUS_BITLEN, STATUS_DEF, STATUS_DEF, False),
]
_registers_map = {r.no: r for r in _registers} # dict map with list comprehension
_registers_name_map = {r.name: r for r in _registers} # dict map with list comprehension
def name_to_no(name):
    if name in _registers_name_map.keys():
        register = _registers_name_map[name]
        return register.no
    else:
        print(f'l6470.name_to_no({name}), no register.')
        return None
def bitlen(no):
    register = _registers_map[no]
    if register == None: print(f'l6470.bitlen({no}), no register.'); return None
    return register.bitlen


###################################
# command definition
###################################
NOP = 0x00
SET_PARAM    = 0x00; SET_PARAM_MASK    = 0xe0; SET_PARAM_PARAM_MASK = 0x1f
GET_PARAM    = 0x20; GET_PARAM_MASK    = 0xe0; GET_PARAM_PARAM_MASK = 0x1f
RUN          = 0x50; RUN_MASK          = 0xfe; RUN_DIR_MASK = 0x01
STEP_CLOCK   = 0x58; STEP_CLOCK_MASK   = 0xfe; STEP_CLOCK_DIR_MASK = 0x01
MOVE         = 0x40; MOVE_MASK         = 0xfe; MOVE_DIR_MASK = 0x01
GOTO         = 0x60; GOTO_MASK         = 0xff
GOTO_DIR     = 0x68; GOTO_DIR_MASK     = 0xfe; GOTO_DIR_DIR_MASK = 0x01
GO_UNTIL     = 0x82; GO_UNITL_MASK     = 0xf2; GO_UNTIL_ACT_MASK = 0x08; GO_UNTIL_DIR_MASK = 0x01
RELEASE_SW   = 0x92; RELEASE_SW_MASK   = 0xf2; RELEASE_SW_ACT_MASK = 0x08; RELEASE_SW_DIR_MASK = 0x01
GO_HOME      = 0x70; GO_HOME_MASK      = 0xff
GO_MARK      = 0x78; GO_MARK_MASK      = 0xff
RESET_POS    = 0xD8; RESET_POS_MASK    = 0xff
RESET_DEVICE = 0xC0; RESET_DEVICE_MASK = 0xff
SOFT_STOP    = 0xB0; SOFT_STOP_MASK    = 0xff
HARD_STOP    = 0xB8; HARD_STOP_MASK    = 0xff
SOFT_HIZ     = 0xA0; SOFT_HIZ_MASK     = 0xff
HARD_HIZ     = 0xA8; HARD_HIZ_MASK     = 0xff
GET_STATUS   = 0xD0; GET_STATUS_MASK   = 0xff; GET_STATUS_BIT_SIZE = 16
# GET_STATUS command resets any warning flags and exits any error states.
# while GET_PARAM(STATUS) does not.

###################################
# common definition
###################################
FWD = 1
REV = 0
HOME_ACTION_CLEAR_ABS_POS = 0
HOME_ACTION_COPY_ABS_POS_TO_MARK = 1

###################################
# status register bits
###################################
STATUS_BIT_HiZ = 0x0001
STATUS_BIT_BUSY = 0x0002 # active low
STATUS_BIT_SW_F = 0x0004
STATUS_BIT_SW_EVN = 0x0008 # latched and cleared by GetStatus command
STATUS_BIT_DIR = 0x0010
STATUS_BIT_MOT_STATUS_0 = 0x0020
STATUS_BIT_MOT_STATUS_1 = 0x0040
STATUS_BIT_NOTPERF_CMD = 0x0080 # latched and cleared by GetStatus command
STATUS_BIT_WRONG_CMD = 0x0100 # latched and cleared by GetStatus command
STATUS_BIT_UVLO = 0x0200 # active low, latched and cleared by GetStatus command
STATUS_BIT_TH_WRN = 0x0400 # active low, latched and cleared by GetStatus command
STATUS_BIT_TH_SD = 0x0800 # active low, latched and cleared by GetStatus command
STATUS_BIT_OCD = 0x1000 # active low, latched and cleared by GetStatus command
STATUS_BIT_STEP_LOSS_A = 0x2000 # active low, latched and cleared by GetStatus command
STATUS_BIT_STEP_LOSS_B = 0x4000 # active low, latched and cleared by GetStatus command
STATUS_BIT_STEP_LOSSES = 0x6000
STATUS_BIT_MOT_STATUS_MASK = 0x0060
STATUS_BIT_MOT_STATUS_STOP = 0x0000
STATUS_BIT_MOT_STATUS_ACC = 0x0020
STATUS_BIT_MOT_STATUS_DEC = 0x0040
STATUS_BIT_MOT_STATUS_CONST_SPEED = 0x0060
# MOT_STATUS_STOP = 0
# MOT_STATS_ACC = 1
# MOT_STATS_DEC = 2
# MOT_STATS_CONST_SPEED = 3

###################################
# config register
###################################
CONFIG_DEFAULT_VALUE     = 0x2e88
CONFIG_SW_MODE_MASK      = 0x0010 # Mask for this bit.
CONFIG_SW_MODE_HARD_STOP = 0x0000 # Default; hard stop motor on switch.
CONFIG_SW_MODE_USER      = 0x0010 # soft stop on GoUntil


###################################
# config values.
###################################
STEP_FS   = 0x00 # one step per full step
STEP_FS_2 = 0x01 # two microsteps per full step
STEP_FS_4 = 0x02 # four microsteps per full step
STEP_FS_8 = 0x03 # etc.
STEP_FS_16= 0x04
STEP_FS_32= 0x05
STEP_FS_64= 0x06
STEP_FS_128= 0x07

###################################
# position range
###################################
MAX_POS = pow(2, 21) - 1
MIN_POS = -pow(2, 22)
def clamp_pos(pos):
    if pos > MAX_POS: pos = MAX_POS
    elif pos < MIN_POS: pos = MIN_POS
    return pos

#l6470.py
