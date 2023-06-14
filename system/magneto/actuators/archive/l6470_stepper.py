###############################################################################
# l6470_stepper.py
###############################################################################
import math
# from L6470.SC18IS602B import SC18IS602B
from interface import Interface

#import magneto.stepper.l6470 as l6470
import l6470 as l6470

###############################################################################
# L6470 stepper driver class
###############################################################################
class L6470Stepper():
    ###################################
    # __init__
    ###################################
    def __init__(self, interface):
        self.interface = interface
        self.reset_device()
        self.clear_status() # clears UVLO bit flag

    ###################################
    # set/get register
    ###################################
    def get_register(self, no):
        self.interface.xfer_cmd(l6470.GET_PARAM | no)
        bitlen = l6470.bitlen(no)
        return self.interface.xfer_param(0, bitlen)
    def set_register(self, no, value):
        self.interface.xfer_cmd(l6470.SET_PARAM | no)
        bitlen = l6470.bitlen(no)
        self.interface.xfer_param(value, bitlen)

    ###################################
    # motion commands
    ###################################
    def move(self, micro_steps, direction):
        micro_steps = int(micro_steps)
        micro_steps = l6470.clamp_pos(micro_steps)
        self.interface.xfer_cmd(l6470.MOVE | direction)
        self.interface.xfer_param(micro_steps, l6470.ABS_POS_BITLEN)
    def go_to(self, micro_steps):
        ''' goes to pos in shortest way.
        pos in absolute but not relative, unlike move command'''
        micro_steps = int(micro_steps)
        micro_steps = l6470.clamp_pos(micro_steps)
        self.interface.xfer_cmd(l6470.GOTO)
        self.interface.xfer_param(micro_steps, l6470.ABS_POS_BITLEN)
    def go_to_dir(self, direction, micro_steps):
        micro_steps = int(micro_steps)
        micro_steps = l6470.clamp_pos(micro_steps)
        self.interface.xfer_cmd(l6470.GOTO_DIR | direction)
        self.interface.xfer_param(micro_steps, l6470.ABS_POS_BITLEN)

    ###################################
    # home commands
    ###################################
    def go_home(self):
        self.interface.xfer_byte_data(l6470.GO_HOME)
    def go_until(self, action, direction, motor_steps_per_sec):
        '''
        GoUntil will ... the ABS_POS register is reset (if ACT = '0') or
        the ABS_POS register value is copied into the MARK register (if ACT = '1');
        falling edge is detected on the SW pin
        '''
        speed = self._calc_speed(motor_steps_per_sec)
        self.interface.xfer_cmd(l6470.GO_UNTIL | action | direction)
        self.interface.xfer_param(speed, l6470.SPEED_BITLEN)
    def release_switch(self, action, direction):
        '''
        Similar in nature to GoUntil, ReleaseSW produces motion at the
        higher of two speeds: the value in MIN_SPEED or 5 steps/s.
        switch input: rising edge
        '''
        self.interface.xfer_cmd(l6470.RELEASE_SW | action | direction)
    def set_switch_mode(self, switch_mode):
        '''
        The switch input can either hard-stop the driver _or_ activate an interrupt.
        This bit allows you to select what it does.
        CONFIG_SW_HARD_STOP or CONFIG_SW_USER
        '''
        config = self.get_register(l6470.CONFIG)
        config &= ~(l6470.CONFIG_SW_MODE_MASK)
        config |= switch_mode
        self.set_register(l6470.CONFIG, config)
    def get_switch_mode(self):
        return int(self.get_register(l6470.CONFIG) & l6470.CONFIG_SW_MODE_MASK)

    ###################################
    # reset, stop
    ###################################
    def reset_device(self):
        self.interface.xfer_cmd(l6470.RESET_DEVICE)
    def soft_stop(self):
        self.interface.xfer_cmd(l6470.SOFT_STOP)
    def hard_stop(self):
        self.interface.xfer_cmd(l6470.HARD_STOP)

    ###################################
    # status
    ###################################
    def get_status(self):
        return self.get_register(l6470.STATUS)
    def clear_status(self):
        # get status command resets any warning flags and exits any error states.
        self.interface.xfer_cmd(l6470.GET_STATUS)
        return self.interface.xfer_param(0, l6470.GET_STATUS_BIT_SIZE)
    def is_busy(self):
        return not (self.get_status() & l6470.STATUS_BIT_BUSY)
    def is_switch_on(self):
        return (self.get_status() & l6470.STATUS_BIT_SW_F)
    def is_motion_stop(self):
        motion_bits = self.get_status() & l6470.STATUS_BIT_MOT_STATUS_MASK
        if motion_bits == l6470.STATUS_BIT_MOT_STATUS_STOP: return True
        else: return False

    ###################################
    # position commands
    ###################################
    def get_pos(self):
        pos = self.get_register(l6470.ABS_POS)
        if pos & 0x00200000:
            pos |= 0xffc00000
        return pos | (-(pos & 0x80000000))  # conver to signed int32
    def reset_pos(self):
        self.interface.xfer_cmd(l6470.RESET_POS)

    ###################################
    # step mode
    ###################################
    def set_step_mode(self, step_mode):
        current_reg_value = self.get_register(l6470.STEP_MODE)
        current_reg_value &= 0xF8 # mask out step mode field
        current_reg_value |= ( step_mode & 0x07) # set step mode keeping other field
        self.set_register(l6470.STEP_MODE, current_reg_value)
    def get_step_mode(self):
        return self.get_register(l6470.STEP_MODE) & 0x07
    def get_micro_steps(self):
        step_mode = self.get_register(l6470.STEP_MODE) & 0x07
        if step_mode == l6470.STEP_FS: return 1
        elif step_mode == l6470.STEP_FS_2: return 2
        elif step_mode == l6470.STEP_FS_4: return 4
        elif step_mode == l6470.STEP_FS_8: return 8
        elif step_mode == l6470.STEP_FS_16: return 16
        elif step_mode == l6470.STEP_FS_32: return 32
        elif step_mode == l6470.STEP_FS_64: return 64
        elif step_mode == l6470.STEP_FS_128: return 128
        else: return 1

    ###################################
    # speed commands
    ###################################
    ''' The value in the MAX_SPD register is [(steps/s)*(tick)]/(2^-18) where tick is 
    250 ns (datasheet value)- 0x041 on boot.
    Multiply desired steps/s by .065536 to get an appropriate value for this register
    This is a 10-bit value, so we need to make sure it remains at or below 0x3FF '''
    def _calc_max_speed(self, motor_steps_per_sec):
        reg_value = math.ceil(motor_steps_per_sec*0.065536)
        if reg_value > 0x000003FF:
            reg_value = 0x000003FF
        return reg_value
    def _parse_max_spped(self, reg_value):
        return float( (reg_value & 0x000003FF) / 0.065536 )
    def set_max_speed(self, motor_steps_per_sec):
        # set max speed steps/s. steps are independent of step mode.
        reg_value = self._calc_max_speed(motor_steps_per_sec)
        self.set_register(l6470.MAX_SPEED, reg_value)
    def get_max_speed(self):
        return int(self._parse_max_spped(self.get_register(l6470.MAX_SPEED)))
    ''' The value in the MIN_SPD register is [(steps/s)*(tick)]/(2^-24) where tick is 
    250 ns (datasheet value)- 0x000 on boot.
    Multiply desired steps/s by 4.1943 to get an appropriate value for this register
    is a 12-bit value, so we need to make sure the value is at or below 0xFFF. '''
    def _calc_min_speed(self, motor_steps_per_sec):
        reg_value = math.ceil(motor_steps_per_sec / 0.238)
        if reg_value > 0x00000FFF:
            reg_value = 0x00000FFF
        return reg_value
    def _parse_min_speed(self, reg_value):
        return float( (reg_value & 0x00000FFF) * 0.238 )
    ''' Set the minimum speed allowable in the system. This is the speed a motion
    starts with; it will then ramp up to the designated speed or the max
    speed, using the acceleration profile. '''
    def set_min_speed(self, motor_steps_per_sec):
        reg_value = self._calc_min_speed(motor_steps_per_sec)
        # MIN_SPEED also contains the LSPD_OPT flag, so we need to protect that.
        temp = self.get_register(l6470.MIN_SPEED) & 0x00001000
        # Now, we can set that paramter.
        self.set_register(l6470.MIN_SPEED, reg_value | temp)
    def get_min_speed(self):
        return self._parse_min_speed(self.get_register(l6470.MIN_SPEED))
    ''' The value in the ACC register is [(steps/s/s)*(tick^2)]/(2^-40) where tick is 
    250 ns (datasheet value)- 0x08A on boot.
    Multiply desired steps/s/s by .137438 to get an appropriate value for this register.
    This is a 12-bit value, so we need to make sure the value is at or below 0xFFF. '''
    def _calc_acc(self, motor_steps_per_sec_per_sec):
        reg_value = math.ceil(motor_steps_per_sec_per_sec * 0.137438)
        if ( reg_value > 0x00000FFF): reg_value = 0x00000FFF
        return reg_value
    def _parse_acc(self, reg_value):
        return float( (reg_value & 0x00000FFF) / 0.137438)
    ''' Set the acceleration rate, in steps per second per second. This value is
    converted to a dSPIN friendly value. Any value larger than 29802 will
    disable acceleration, putting the chip in "infinite" acceleration mode. '''
    def set_acc(self, motor_steps_per_sec_per_sec):
        reg_value = self._calc_acc(motor_steps_per_sec_per_sec)
        if reg_value > 4095: reg_value = 4094
        self.set_register(l6470.ACC, reg_value)
    def get_acc(self):
        return self._parse_acc(self.get_register(l6470.ACC))
    ''' The calculation for DEC is the same as for ACC. Value is 0x08A on boot.
     This is a 12-bit value, so we need to make sure the value is at or below 0xFFF. '''
    def set_dec(self, motor_steps_per_sec_per_sec):
        reg_value = self._calc_acc(motor_steps_per_sec_per_sec)
        if reg_value > 4095: reg_value = 4094
        self.set_register(l6470.DEC, reg_value)
    def get_dec(self):
        return self._parse_acc(self.get_register(l6470.DEC))
    ''' When issuing RUN command, the 20-bit speed is [(steps/s)*(tick)]/(2^-28) where tick is 
    250 ns (datasheet value).
    Multiply desired steps/s by 67.106 to get an appropriate value for this register
    This is a 20-bit value, so we need to make sure the value is at or below 0xFFFFF.'''
    def _calc_speed(self, motor_steps_per_sec):
        reg_value = int(motor_steps_per_sec * 67.106)
        if(reg_value > 0x000FFFFF):
            reg_value = 0x000FFFFF
        return reg_value
    def _parse_speed(self, reg_value):
        return float((reg_value & 0x000FFFFF) / 67.106)
    def get_speed(self):
        speed = self._parse_speed(self.get_register(l6470.SPEED))
        if self.is_motion_stop(): speed = 0
        return speed


    ###################################
    # over current
    ###################################
    def set_oc_threshold(self, threshold):
        self.set_register(l6470.OCD_TH, 0x0F & threshold)
    def get_oc_threshold(self):
        return (self.get_register(l6470.OCD_TH) & 0xF)
    def set_oc_shutdown(self, shutdown):
        ''' needs refactoring with mask bit '''
        config_val = self.get_register(l6470.CONFIG)
        config_val &= ~(0x0080) # bit 7
        config_val |= (0x0080 & shutdown)
        self.set_register(l6470.CONFIG, config_val)
    def get_oc_shutdown(self):
        return self.get_register(l6470.CONFIG) & 0x0080

    ###################################
    # stall threshold
    ###################################
    def set_stall_th(self, threshold):
        ''' The STALL_TH register contains the stall detection threshold value (see Section 7.2 on
        page 35).The available range is from 31.25 mA to 4 A with a resolution of 31.25 mA.
        (Val. + 1) * 31.25 = Stall detection threshold mA '''
        self.set_register(l6470.STALL_TH, threshold)
    def get_stall_th(self):
        return self.get_register(l6470.STALL_TH)

    ###################################
    # high z stop
    ###################################
    def soft_hi_z(self):
        self.interface.xfer_byte_data(l6470.SOFT_HIZ)
    def hard_hi_z(self):
        # Put the bridges in Hi-Z state immediately with no deceleration.
        self.interface.xfer_byte_data(l6470.HARD_HIZ)

    ###################################
    # etc
    ###################################
    def print_registers(self):
        print('Register Values')
        for register in l6470._registers:
            print(f'{register.name}, {hex(self.get_register(register.no))}')

#l6470_stepper.py
