###############################################################################
# filter.py
# - L6470 switch mode must be set to user mode not hard stop mode
###############################################################################
import math
from time import sleep
import magneto.actuators.l6470 as l6470
from magneto.actuators.l6470_stepper import L6470Stepper

###############################################################################
# Filter class based on L6470 stepper
###############################################################################
class Filter(L6470Stepper):
    ###################################
    # __init__
    ###################################
    def __init__(self, interface):
        super().__init__(interface)
        self.reset()
        # check L6470 driver
        if self.get_register(l6470.CONFIG) != l6470.CONFIG_DEFAULT_VALUE:
            print(f'Filter driver not detected.')
            raise(SystemExit)
        self._init_params()
        print(f'Filter initialized')

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
        super().set_register(no, value)

    def get_pos(self):
        return self._micro_steps_to_deg(super().get_pos())
 
    def wait(self):
        # print(f'encoder pos: {self.get_abs_pos()}, stepper pos: {self.get_pos()}')
        return super().is_busy()

    def jog(self, direction, shift=None):
        if shift == None:
            shift = self.jog_shift
        if direction == '+':
            direction = l6470.FWD
        else:
            direction = l6470.REV
        super().move(self._deg_to_micro_steps(shift), direction)

    def set_pos(self, pos):
        super().set_register(l6470.ABS_POS, self._deg_to_micro_steps(pos), signed=True)

    def go_until(self):
        if super().is_switch_on():
            return
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode
        super().set_max_speed(self._deg_to_motor_steps(self.go_until_speed)) # necessary to avoid clamping by low max
        super().go_until(action=l6470.HOME_ACTION_CLEAR_ABS_POS, direction=self.go_until_direction,
                         motor_steps_per_sec=self._deg_to_motor_steps(self.go_until_speed))

    def release_switch(self):
        if not super().is_switch_on():
            return
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode
        super().release_switch(action=l6470.HOME_ACTION_CLEAR_ABS_POS,
                               direction=self.release_switch_direction)

    def home_shift(self):
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode
        super().set_max_speed(self._deg_to_motor_steps(self.go_until_speed))
        super().move(self._deg_to_micro_steps(self.home_shift_amount),
                     self.home_shift_direction)

    def position(self, position):
        super().set_max_speed(self._deg_to_motor_steps(self.max_speed))
        super().go_to(self._deg_to_micro_steps(position))

    def goto(self, no):
        interval = 360 / self.max_filter_no
        position = interval * (no - 1)
        print(f'goto():{position}, {self._deg_to_micro_steps(position)}')
        super().set_max_speed(self._deg_to_motor_steps(self.goto_speed))
        super().go_to(self._deg_to_micro_steps(position))

    def stop(self):
        self.hard_stop()

    def hard_stop(self):
        super().hard_stop()

    def soft_stop(self):
        super().soft_stop()

    def reset(self):
        super().reset_device()
        super().clear_status()

    ###################################
    # init params
    ###################################
    def _init_params(self):
        self.motor_steps_per_rev = 200 # common step motor
        self.set_step_mode(l6470.STEP_FS_128)  # common step motor
        self.micro_steps = super().get_micro_steps()
        self.micro_steps_per_rev = self.motor_steps_per_rev * self.micro_steps
        self.gear_ratio = 1  # default
        self.home_pos = 0 # [deg]
        # self.home_pos = -55 # [deg] PG35S-D48-HHC2
        # self.home_shift_amount = 5 # [deg], backlash tracking
        # self.backlash = 1.4 # [deg] PG35S-D48-HHC2
       
        self.max_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
        self.min_speed = 10  # [deg/s], considering any shock during start or stop
        acc = self.max_speed * 10  # [deg/s/s], 0.1 s to max speed
        dec = acc
        self.set_max_speed(self._deg_to_motor_steps(self.max_speed))
        self.set_min_speed(self._deg_to_motor_steps(self.min_speed))
        self.set_acc(self._deg_to_motor_steps(acc))
        self.set_dec(self._deg_to_motor_steps(dec))

        super().set_stall_th(127) # max 127

        self.set_register(l6470.KVAL_ACC, 90)
        self.set_register(l6470.KVAL_DEC, 90)
        self.set_register(l6470.KVAL_RUN, 90)
        self.set_register(l6470.KVAL_HOLD,20)

        # self.set_register(l6470.KVAL_ACC, 120)
        # self.set_register(l6470.KVAL_DEC, 120)
        # self.set_register(l6470.KVAL_RUN, 120)
        # self.set_register(l6470.KVAL_HOLD,20)

        # self.set_register(l6470.KVAL_ACC, 200)
        # self.set_register(l6470.KVAL_DEC, 200)
        # self.set_register(l6470.KVAL_RUN, 200)
        # self.set_register(l6470.KVAL_HOLD,20)

        self.go_until_speed = self.max_speed  # [deg/s]
        self.go_until_direction = l6470.FWD
        self.release_switch_direction = l6470.REV
        self.home_shift_direction = self.release_switch_direction
        ''' home relase switch speed = max(min speed or 5 motor-steps/s)
        [deg], # shift after release switch to ensure that the switch is off enough '''
        self.home_shift_amount = 5 #[deg]
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode

        # goto command
        self.min_filter_no = 1
        self.max_filter_no = 4
        self.goto_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s

    ###################################
    # uint conversion
    ###################################
    def _deg_to_micro_steps(self, deg):
        return int(deg / 360.0 * self.micro_steps_per_rev * self.gear_ratio)

    def _micro_steps_to_deg(self, micro_steps):
        return micro_steps * 360.0 / self.micro_steps_per_rev / self.gear_ratio

    def _deg_to_motor_steps(self, deg):
        return int(deg / 360.0 * self.motor_steps_per_rev * self.gear_ratio)

    def _motor_steps_to_degree(self, motor_steps):
        return motor_steps * 360.0 / self.motor_steps_per_rev / self.gear_ratio


# filter.py
