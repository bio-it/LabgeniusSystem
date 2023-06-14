# -*- coding: utf-8 -*-
###############################################################################
# chamber_emulator.py
###############################################################################
import magneto.actuators.l6470 as l6470
import time


class BusyClearException(Exception):
    pass


class ChamberEmulator():
    def __init__(self):
        self.busy_end_time = time.time()  # emulator only
        # self.stop_request = False
        print(f'chamber emulator initialized')
        # for ch in range(1, 26+1):
        #     print(f'ch no={ch}, ch pos={self._no_to_deggree(ch)}')

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
        return 123.4

    def set_encoder_zero_position(self):
        print(f"ChamberEmulator.set_encoder_zero_position()")

    def update_encoder_multi_turn(self):
        pass

    def get_min_chamber_no(self):
        return 1

    def get_max_chamber_no(self):
        return 13

    def get_register(self, no):
        return 123

    def set_register(self, no, value):
        pass

    def get_status(self):
        return 0xffff

    def get_pos(self):
        return 123.456

    def wait(self):
        if time.time() >= self.busy_end_time:  # emulator only
            return False  # not waiting
        return True  # waiting

    def jog(self, direction, shift=None):
        self.busy_end_time = time.time() + 2
        print(f"ChamberEmulator.jog({direction}, {shift})")

    # def move(self, position):
    #     self.busy_end_time = time.time() + 2
    #     print(f"ChamberEmulator.move({position})")

    # def home(self):
    #     self.busy_end_time = time.time() + 2
    #     print(f"ChamberEmulator.home()")

    # def go_until(self):
    #     self.busy_end_time = time.time() + 2
    #     print(f"ChamberEmulator.go_until()")

    # def release_switch(self):
    #     self.busy_end_time = time.time() + 2
    #     print(f"ChamberEmulator.release_switch())")

    # def home_shift(self):
    #     self.busy_end_time = time.time() + 2
    #     print(f"ChamberEmulator.home_shift())")

    def set_pos(self, pos):
        print(f"ChamberEmulator.set_pos())")

    def goto_home(self):
        self.busy_end_time = time.time() + 2
        print(f"ChamberEmulator.goto_home())")

    def sync_with_encoder_position(self):
        print(
            f'chamber sync_with_encoder_position, enc pos={self.get_encoder_position()}, pos={self.get_pos()}')

    def set_driver_position_to_zero(self):
        print(f"ChamberEmulator.set_driver_position_to_zero())")

    def goto(self, no):
        self.busy_end_time = time.time() + 2
        print(f"ChamberEmulator.goto({no}))")

    def position(self, position):
        self.busy_end_time = time.time() + 2
        print(f"ChamberEmulator.position({position}))")

    def stop(self):
        print(f"ChamberEmulator.stop()")
        self.busy_end_time = time.time()

    def hard_stop(self):
        print(f"ChamberEmulator.hard_stop()")
        self.busy_end_time = time.time()

    def soft_stop(self):
        print(f"ChamberEmulator.soft_stop()")
        self.busy_end_time = time.time()

    def reset(self):
        print(f"ChamberEmulator.reset()")
        self.busy_end_time = time.time()

    def clear_status(self):
        print(f"ChamberEmulator.clear_status()")

    '''
    mechanical considerations:
    - from top view, (+) direction is CW and (-) direction is CCW
    - from top view
            ======
            13
        12     |    1
    11         |th/eta 2
   10          |/
               --------  3
    9                    
       8               4
           7       5
                6
              ===
    - chamber 6: sample reservoir, with a large hole
    - chamber 13: no physical chamber, connected to chip
    - theta - 20.77 deg
    '''

    def _no_to_deggree(self, chamber_no):
        theta = 20.77 + 10
        ch_3_pos = 90.0 - theta
        chamber_no_diff = chamber_no - 3
        # ch_3_pos = 0
        pos = chamber_no_diff * 360.0 / 13
        pos = pos + ch_3_pos
        if pos > 360.0:
            pos = pos - 360
        return pos

# chamber_emulator.py
