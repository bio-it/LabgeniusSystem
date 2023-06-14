import magneto.stepper.l6470 as l6470
import time

class StopRequestException(Exception):
    pass


class BusyClearException(Exception):
    pass


class DummyStepper():
    def __init__(self):
        self.busy_end_time = 0  # dummy only
        self.home_step = -1
        self.stop_request = False

    def get_min_no(self):  # chamber only
        return 1

    def get_max_no(self):  # chamber only
        return 13

    def get_register(self, reg_no):
        return 123

    def set_register(self, reg_name, reg_value):
        pass

    def get_pos(self):
        return 123.456

    def get_speed(self):
        return 456.789

    def get_acc(self):
        return 606.707

    def get_dec(self):
        return 808.909

    def _check_stop_request(self):
        if self.stop_request:
            self.stop_request = False
            self.busy_end_time = time.time() # dummy only
            self.home_step = -1
            raise StopRequestException

    def _check_busy(self):
        if time.time() >= self.busy_end_time:
            raise BusyClearException

    def wait(self):
        try:
            self._check_stop_request()
            self._check_busy()
            return True  # waiting
        except (StopRequestException, BusyClearException):
            return False  # not waiting

    def jog(self, direction):
        self.busy_end_time = time.time() + 2
        print(f"DummyStepper.jog({direction})")

    def move(self, position):
        self.busy_end_time = time.time() + 2
        print(f"DummyStepper.move({position})")

    def go_until(self, direction):
        self.busy_end_time = time.time() + 3
        print(f"DummyStepper.go_until({direction})")

    def release_switch(self, direction):
        self.busy_end_time = time.time() + 1
        print(f"DummyStepper.release_switch({direction})")

    def home(self):
        self.busy_end_time = time.time() + 3
        print(f"DummyStepper.go_until(fwd)")
        self.home_step = 0
    def home_wait(self):
        if self.home_step == 0:
            return self.home_step_0() # wait go until, start release switch
        elif self.home_step == 1:
            return self.home_step_1() # wait release switch, start shift move
        elif self.home_step == 2:
            return self.home_step_2() # wait shift move
    def home_step_0(self):
        # wait go until
        if self.wait(): return True
        # start relese switch
        self.busy_end_time = time.time() + 1
        print(f"DummyStepper.release_switch(rev)")
        self.home_step = 1
        return True
    def home_step_1(self):
        # wait release switch
        if self.wait(): return True
        # start shift move
        self.busy_end_time = time.time() + 2
        print(f"DummyStepper.move(rev)")
        self.home_step = 2
        return True
    def home_step_2(self):
        # wait shift move
        if self.wait(): return True
        # finish home
        self.home_step = 0
        return False

    def hard_stop(self):
        print(f"DummyStepper.hard_stop()")
        self.stop_request = True

    def soft_stop(self):
        print(f"DummyStepper.soft_stop()")
        self.stop_request = True

    def reset(self):
        print(f"DummyStepper.reset()")
        self.stop_request = True

    def clear_status(self):
        print(f"DummyStepper.clear_status()")
