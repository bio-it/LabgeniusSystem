# -*- coding: utf-8 -*-
###############################################################################
# syringe_emulator.py
###############################################################################
import time
import magneto.actuators.l6470 as l6470


class SyringeEmulator():
    def __init__(self):
        self.busy_end_time = time.time()  # emulator only
        self._load_bottom_position()
        print(f'syringe emulator initialized')

    def get_registers(self):
        registers = {r.name: r.value for r in l6470._registers}
        for name in registers.keys():
            no = l6470.name_to_no(name)
            value = self.get_register(no)
            registers[name] = value
        return registers

    def is_busy(self):
        return self.wait()

    def get_encoder_position(self):
        return 456.7

    def set_encoder_zero_position(self):
        print(f"SyringeEmulator.set_encoder_zero_position()")

    def update_encoder_multi_turn(self):
        pass

    def get_register(self, no):
        return 234

    def set_register(self, no, value):
        print(f"SyringeEmulator.set_register({no}, {value})")
        pass

    def get_status(self):
        return 0xffff

    def get_pos(self):
        return 567.8

    def wait(self):
        if time.time() >= self.busy_end_time:
            return False  # not waiting
        return True  # waiting

    def jog(self, direction, shift=None):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.jog({direction}, {shift})")

    def move(self, position):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.move({position})")

    def go_until(self):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.go_until()")

    def release_switch(self):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.release_switch()")

    def home_shift(self):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.home_shift()")

    def position(self, position):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.position({position})")

    def volume(self, volume):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.volume({volume})")

    def pumping(self, action, volume):
        self.busy_end_time = time.time() + 2
        print(f"SyringeEmulator.pumping({action}, {volume})")

    def stop(self):
        print(f"SyringeEmulator.stop()")
        self.busy_end_time_count = time.time()

    def hard_stop(self):
        print(f"SyringeEmulator.hard_stop()")
        self.busy_end_time_count = time.time()

    def soft_stop(self):
        print(f"SyringeEmulator.soft_stop()")
        self.busy_end_time_count = time.time()

    def reset(self):
        print(f"SyringeEmulator.reset()")
        self.busy_end_time_count = time.time()

    def clear_status(self):
        print(f"SyringeEmulator.clear_status()")

    def save_bottom_position(self):
        try:
            file_name = "./syringe_bottom_pos.txt"
            with open(file_name, "w") as f:
                f.write(f'{self.get_pos()}')
                print(f'save_bottom_pos, {self.get_pos()}')
        except IOError:
            print('syringe bottom position save failed')

    def _load_bottom_position(self):
        try:
            file_name = "./syringe_bottom_pos.txt"
            with open(file_name, "r") as f:
                pos = f.readline()
                print(f'_load_bottom_pos, {pos}')
        except IOError:
            print('syringe bottom position load failed')
            print(f'syringe bottom position set with default value {45.123}')


# syringe_emulator.py
