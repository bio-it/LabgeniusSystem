Skip to content
Search or jump to…

Pull requests
Issues
Marketplace
Explore
 
@munhoryu 
munhoryu
/
extractor_server
Private
1
00
Code
Issues
Pull requests
Actions
Projects
Security
Insights
Settings
extractor_server/magneto/stepper/syringe.py /
@munhoryu
munhoryu _Working dummy_Han_
Latest commit 5d6f2ab on 27 Oct 2020
 History
 1 contributor
70 lines (64 sloc)  2.65 KB
  
###############################################################################
# syringe.py
###############################################################################
import math
from time import sleep

import magneto.stepper.l6470 as l6470
from magneto.stepper.sc18is602b import SC18IS602B
from magneto.stepper.l6470_stepper import L6470Stepper
from magneto.stepper.stepper import Stepper, StepperParams

###############################################################################
# Syringe class based on L6470 Stepper
###############################################################################
params = StepperParams()
params.name = 'syringe'
params.linear = True
params.motor_steps_per_rev = 200
params.full_step = l6470.STEP_FS_128
params.max_speed = 5.0  # [mm/s], 5 mm in 1 s
params.min_speed = 1.0  # [mm/s], considering any shock during start or stop
params.acc = params.max_speed * 10  # [mm/s/s], 0.1 s to max speed
params.dec = params.acc
params.kval_acc = 50
params.kval_dec = 50
params.kval_run = 50
params.kval_hold = 20
params.go_until_speed = params.max_speed / 2  # [mm/s], half max_speed
params.go_until_direction = l6470.REV
params.release_switch_direction = l6470.FWD
params.home_shift_direction = params.release_switch_direction
# home relase switch speed = max(min speed or 5 motor-steps/s)
# [mm], # shift after release switch to ensure that the switch is off enough
params.home_shift = 1
params.jog_shift = 1  # [mm]
# linear only
params.lead = 1.0  # 1 mm / 1 rev

class Syringe(Stepper):
    # mechanical properties
    bottom_pos = 10.0 # 60.69 # [mm]
    top_pos = 0.0 # 28.00 # [mm]
    up_offset = -1.75 # [mm]
    disk_radius = 3.0 # [mm]
    # pumping speed
    pumping_speed = 2.0 # [mm/s], 2.0 rev/s, 6.25 rev/s
    slow_pumping_speed = 1.25 # [mm/s], 1.25 rev/s

    def __init__(self, interface):
        super().__init__(interface, params)

    def pumping(self, action, volume):
        # set speed
        if action == 'sup' or action == 'sdown':
            super().set_max_speed(super()._unit_to_motor_steps(self.slow_pumping_speed))
        else:
            super().set_max_speed(super()._unit_to_motor_steps(self.pumping_speed))
        # calculate volume position
        volume_distance = self._volume_to_distance(volume)
        position = self.bottom_pos - volume_distance
        if position < self.top_pos:
            position = self.top_pos
        # start pumping motion
        super().go_to(super()._unit_to_micro_steps(position))

    def _volume_to_distance(self, volume):
        # convert volume to distance in mm
        volume_distance = volume / (math.pi * self.disk_radius * self.disk_radius)
        return volume_distance
#syringe.py
© 2021 GitHub, Inc.
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
Loading complete