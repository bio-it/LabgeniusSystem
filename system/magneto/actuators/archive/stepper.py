###############################################################################
# stepper.py
# common stepper for chamber and syringe
###############################################################################
import math
from time import sleep

import magneto.stepper.l6470 as l6470
from magneto.stepper.sc18is602b import SC18IS602B
from magneto.stepper.l6470_stepper import L6470Stepper

###############################################################################
# Chamber class based on L6470 Stepper
###############################################################################
class StopRequestException(Exception):
    pass
class BusyClearException(Exception):
    pass
class StepperParams():
    def __init__(self):
        self.name = 'unkown stepper'
        self.linear = True
        self.motor_steps_per_rev = 200
        self.step_mode = l6470.STEP_FS_128
        self.max_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
        self.min_speed = 10  # [deg/s], considering any shock during start or stop
        self.acc = self.max_speed * 10  # [deg/s/s], 0.1 s to max speed
        self.dec = self.acc
        self.kval_acc= 50
        self.kval_dec= 50
        self.kval_run= 50
        self.kval_hold= 20
        self.go_until_speed = self.max_speed / 2  # [deg/s], half max_speed
        self.go_until_direction = l6470.FWD
        self.release_switch_direction = l6470.REV
        self.home_shift_direction = self.release_switch_direction
        # home relase switch speed = max(min speed or 5 motor-steps/s)
        self.home_shift = 30  # [deg], # shift after release switch to ensure that the switch is off enough
        self.jog_shift = 90  # [deg]
        # linear only
        self.lead = 1.0  # 1 mm / 1 rev
        # rotary only
        self.gear_ratio = 1.0

class Stepper(L6470Stepper):
    def __init__(self, interface, params):
        self.params = params
        super().__init__(interface)
        self.reset()
        if self.get_register(l6470.CONFIG) != l6470.CONFIG_DEFAULT_VALUE:
            print(f'{self.params.name} driver not detected.')
            raise(SystemExit)
        self.home_step = -1
        self.stop_request = False
        print(f'{self.params.name} initialized')
    def get_pos(self):
        return self._micro_steps_to_unit(super().get_pos())
    def _check_stop_request(self):
        if self.stop_request:
            self.stop_request = False
            #self.home_step = -1
            raise StopRequestException
    def _check_busy(self):
        if not super().is_busy():
            raise BusyClearException
    def wait(self):
        try:
            self._check_stop_request()
            self._check_busy()
            return True  # waiting
        except (StopRequestException, BusyClearException):
            return False  # not waiting
    def jog(self, direction):
        super().move(self._unit_to_micro_steps(self.params.jog_shift), direction)
    def move(self, position):
        super().go_to(self._unit_to_micro_steps(position))

    def go_until(self, direction):
        if super().is_switch_on(): return
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER) # go until mode
        super().go_until(action=l6470.HOME_ACTION_CLEAR_ABS_POS, direction=direction,
                         motor_steps_per_sec=self._unit_to_motor_steps(self.params.go_until_speed))
    def go_until_wait(self):
        busy = self.wait()
        if not busy:
            super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode
        return busy
    def release_switch(self, direction):
        super().release_switch(action=l6470.HOME_ACTION_CLEAR_ABS_POS, direction=direction)
    def home(self):
        # return with wait state = Flase if already on home switch
        if super().is_switch_on(): return False
        # set switch mode to go until mode
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode
        # start go until
        super().go_until(action=l6470.HOME_ACTION_CLEAR_ABS_POS, 
                        direction=self.params.go_until_direction,
                        motor_steps_per_sec=self._unit_to_motor_steps(self.params.go_until_speed))
        # set to next step
        self.home_step = 0
    def home_wait(self):
        if self.home_step == 0:
            return self.home_step_0()  # wait go until, start release switch
        elif self.home_step == 1:
            return self.home_step_1()  # wait release switch, start shift move
        elif self.home_step == 2:
            return self.home_step_2()  # wait shift move
    def home_step_0(self):
        # return with wait state = True if still go until
        if self.wait(): return True
        # restore switch mode to hard stop mode
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode
        # start release switch
        super().release_switch(action=l6470.HOME_ACTION_CLEAR_ABS_POS,
                    direction=self.params.release_switch_direction)
        # set to next step
        self.home_step = 1
        return True
    def home_step_1(self):
        # return with wait state = True if still go until
        if self.wait(): return True
        # start shift back move
        super().move(self._unit_to_micro_steps(self.params.home_shift), 
                    self.params.home_shift_direction)
        # set to next step
        self.home_step = 2
        return True
    def home_step_2(self):
        # return wait state = True if still shift  move
        if self.wait(): return True
        # clear home step
        self.home_step = -1
        # return home sequence finished
        return False
    def stop_home(self):
        self.home_step = -1

    def hard_stop(self):
        super().hard_stop()
        self.stop_request = True
        self.stop_home()
    def soft_stop(self):
        super().soft_stop()
        self.stop_request = True
        self.stop_home()
    def reset(self):
        super().reset_device()
        super().clear_status()
        self.stop_request = True
        self.stop_home()
        self.init_params()

    def init_params(self):
        self.set_register(l6470.KVAL_ACC, self.params.kval_acc)
        self.set_register(l6470.KVAL_DEC, self.params.kval_dec)
        self.set_register(l6470.KVAL_RUN, self.params.kval_run)
        self.set_register(l6470.KVAL_HOLD, self.params.kval_hold)
        self.set_step_mode(self.params.step_mode)
        self.set_max_speed(self._unit_to_motor_steps(self.params.max_speed))
        self.set_min_speed(self._unit_to_motor_steps(self.params.min_speed))
        self.set_acc(self._unit_to_motor_steps(self.params.acc))
        self.set_dec(self._unit_to_motor_steps(self.params.dec))
        self.params.micro_steps = super().get_micro_steps()
        self.params.micro_steps_per_rev = self.params.motor_steps_per_rev * \
            self.params.micro_steps

    # unit vs micro/motor steps
    def _micro_steps_to_unit(self, micro_steps):
        if self.params.linear: return self._micro_steps_to_mm(micro_steps)
        else: return self._micro_steps_to_deg(micro_steps)
    def _unit_to_micro_steps(self, units):
        if self.params.linear: return self._mm_to_micro_steps(units)
        else: return self._deg_to_micro_steps(units)
    def _motor_steps_to_unit(self, motor_steps):
        if self.params.linear: return self._motor_steps_to_mm(motor_steps)
        else: return self._motor_steps_to_deg(motor_steps)
    def _unit_to_motor_steps(self, units):
        if self.params.linear: return self._mm_to_motor_steps(units)
        else: return self._deg_to_motor_steps(units)
    # linear
    def _micro_steps_to_mm(self, micro_steps):
        return int((micro_steps/self.params.micro_steps_per_rev) * self.params.lead)
    def _mm_to_micro_steps(self, mm):
        return mm / self.params.lead * self.params.micro_steps_per_rev
    def _mm_to_motor_steps(self, mm):
        return mm / self.params.lead * self.params.motor_steps_per_rev
    def _motor_steps_to_mm(self, motor_steps):
        return motor_steps / self.params.motor_steps_per_rev * self.params.lead
    # rotary
    def _deg_to_micro_steps(self, deg):
        return int(deg / 360.0 * self.params.micro_steps_per_rev * self.params.gear_ratio)
    def _micro_steps_to_deg(self, micro_steps):
        return micro_steps * 360.0 / self.params.micro_steps_per_rev / self.params.gear_ratio
    def _deg_to_motor_steps(self, deg):
        return int(deg / 360.0 * self.params.motor_steps_per_rev * self.params.gear_ratio)
    def _motor_steps_to_degree(self, motor_steps):
        return motor_steps * 360.0 / self.params.motor_steps_per_rev / self.params.gear_ratio
    # def _deg_to_micro_steps(self, deg):
    #     return int(deg / 360.0 * self.params.micro_steps_per_rev)
    # def _micro_steps_to_deg(self, micro_steps):
    #     return micro_steps * 360.0 / self.params.micro_steps_per_rev
    # def _deg_to_motor_steps(self, deg):
    #     return int(deg / 360.0 * self.params.motor_steps_per_rev)
    # def _motor_steps_to_degree(self, motor_steps):
    #     return motor_steps * 360.0 / self.params.motor_steps_per_rev
#stepper.py
