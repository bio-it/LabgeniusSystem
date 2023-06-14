###############################################################################
# filter_emulator.py
###############################################################################
import time
import magneto.actuators.l6470 as l6470


class FilterEmulator():
    ###################################
    # __init__
    ###################################
    def __init__(self):
        self.busy_end_time = time.time()  # emulator only
        # self.stop_request = False
        print(f'filter emulator initialized')

    ###################################
    # interface functions
    ###################################
    def get_registers(self):
        registers = {r.name: r.value for r in l6470._registers}
        for name in registers.keys():
            no = l6470.name_to_no(name)
            value = self.get_register(no)
            registers[name] = value
        return registers

    def is_busy(self):
        return self.wait()

    def get_min_filter_no(self):
        return 1

    def get_max_filter_no(self):
        return 4

    def get_register(self, no):
        return 345

    def set_register(self, no, value):
        pass

    def get_status(self):
        return 0xffff

    def get_pos(self):
        return 567.8

    def wait(self):
        if time.time() >= self.busy_end_time:  # emulator only
            return False  # not waiting
        return True  # waiting

    def jog(self, direction, shift=None):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.jog({direction}, {shift})")

    def go_until(self):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.go_until()")

    def release_switch(self):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.release_switch()")

    def home_shift(self):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.home_shift()")

    def position(self, position):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.position({position})")

    def goto(self, no):
        self.busy_end_time = time.time() + 2
        print(f"FilterEmulator.goto({no}))")

    def stop(self):
        print(f"FilterEmulator.stop()")
        self.busy_end_time = time.time()

    def hard_stop(self):
        print(f"FilterEmulator.hard_stop()")
        self.busy_end_time = time.time()

    def soft_stop(self):
        print(f"FilterEmulator.soft_stop()")
        self.busy_end_time = time.time()

    def reset(self):
        print(f"FilterEmulator.reset()")
        self.busy_end_time = time.time()

    def clear_status(self):
        print(f"FilterEmulator.clear_status()")

# filter_emulator.py
