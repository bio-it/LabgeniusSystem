###############################################################################
# chamber.py
###############################################################################
import math
from time import sleep

import magneto.stepper.l6470 as l6470
from magneto.stepper.sc18is602b import SC18IS602B
from magneto.stepper.l6470_stepper import L6470Stepper
from magneto.stepper.stepper import Stepper, StepperParams
#from stepper.stepper import StepperParams


###############################################################################
# Chamber class based on L6470 stepper
###############################################################################
params = StepperParams()
params.name = 'chamber'
params.linear = False
params.motor_steps_per_rev = 200
# params.full_step = l6470.STEP_FS_2 # Loco Magneto
params.full_step = l6470.STEP_FS_128 # test motor
params.max_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
params.min_speed = 10  # [deg/s], considering any shock during start or stop
params.acc = params.max_speed * 10  # [deg/s/s], 0.1 s to max speed
params.dec = params.acc
params.kval_acc= 50
params.kval_dec= 50
params.kval_run= 50
params.kval_hold= 20
params.go_until_speed = params.max_speed / 2  # [deg/s], half max_speed
params.go_until_direction = l6470.FWD
params.release_switch_direction = l6470.REV
params.home_shift_direction = params.release_switch_direction
# home relase switch speed = max(min speed or 5 motor-steps/s)
params.home_shift = 30  # [deg], # shift after release switch to ensure that the switch is off enough
params.jog_shift = 90  # [deg]
# linear only
#params.lead = 1.0  # 1 mm / 1 rev
#params.gear_ratio = 60.0 # Loco Magneto
# params.gear_ratio = 1.0 # tet motor
params.gear_ratio = 35.4 # PG35S-D48-HHC2

class Chamber(Stepper):
    min_no = 1
    max_no = 13
    goto_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
    def __init__(self, interface):
        super().__init__(interface, params)
    def get_min_no(self):
        return self.min_no
    def get_max_no(self):
        return self.max_no
    def goto(self, no):
        interval = 360 / self.max_no
        position = interval * (no - 1)
        super().set_max_speed(self._unit_to_motor_steps(self.goto_speed))
        super().go_to(self._unit_to_micro_steps(position))
#chamber.py
