# -*- coding: utf-8 -*-
###############################################################################
# syringe.py
###############################################################################
import math
from time import sleep
import magneto.actuators.l6470 as l6470
from magneto.actuators.l6470_stepper import L6470Stepper


class Syringe(L6470Stepper):
    ###################################
    # __init__
    ###################################
    def __init__(self, interface, encoder):
        super().__init__(interface)
        self.encoder = encoder
        self.reset()
        self.soft_stop()
        # check L6470 driver
        if self.get_register(l6470.CONFIG) != l6470.CONFIG_DEFAULT_VALUE:
            print(f'Syringe driver not detected.')
            raise(SystemExit)
        self._init_params()
        print(f'Syringe initialized')

        # check encoder
        enc_pos, _ = self.encoder.read_abs_pos()
        if enc_pos == -1:
            print('Syringe abs encoder not detected')
            raise(SystemExit)
        print('Syringe abs encoder detected')

        # encoder multi-turn
        self.prev_encoder_count = self.encoder.get_pos()
        self.encoder_multi_turn_count = self.prev_encoder_count
        self.encoder_position = self.encoder_multi_turn_count * self.lead / 4096

        # load bottom position
        self._load_bottom_position()


    ###################################
    # abs encoder
    ###################################
    def get_encoder_position(self):
        return self.encoder_position

    def set_encoder_zero_position(self):
        self.prev_encoder_count = 0
        self.encoder_multi_turn_count = 0
        self.encoder_position = 0
        self.encoder.set_zero_position()

    def update_encoder_multi_turn(self):
        # calculate delta count
        current_count = self.encoder.get_pos()
        delta_count = current_count - self.prev_encoder_count
        self.prev_encoder_count = current_count
        # check overflow, 4095 -> 1
        if delta_count < -2048:
            delta_count += 4096
        # check underflow, 1 -> 4095
        elif delta_count > 2048:
            delta_count -= 4096 
        # update
        self.encoder_multi_turn_count += delta_count
        # convert count to mm
        self.encoder_position = self.encoder_multi_turn_count * self.lead / 4096

    def print_position(self):
        # print(f'{self.get_encoder_position()}, {self.get_pos()}')
        print(
            f'{self.get_encoder_position()}, {self.get_pos()}, {self.get_encoder_position()-self.get_pos()}')


    ###################################
    # interface functions
    ###################################
    def get_register(self, no):
        return super().get_register(no)

    def set_register(self, no, value):
        super().set_register(no, value)

    def get_pos(self):
        return self._micro_steps_to_mm(super().get_pos())

    def wait(self):
        self.update_encoder_multi_turn()
        return super().is_busy()

    def jog(self, direction, amount=None):
        if amount == None:
            amount = self.jog_amount
        if direction == '+':
            direction = l6470.FWD
        else:
            direction = l6470.REV
        super().set_max_speed(self._mm_to_motor_steps(self.jog_speed))
        super().move(self._mm_to_micro_steps(amount), direction)

    def go_until(self):
        if super().is_switch_on():
            return
        super().set_switch_mode(l6470.CONFIG_SW_MODE_USER)  # go until mode
        super().set_max_speed(self._mm_to_motor_steps(self.go_until_speed)) # necessary to avoid clamping by low max
        super().go_until(action=l6470.HOME_ACTION_CLEAR_ABS_POS, direction=self.go_until_direction,
                         motor_steps_per_sec=self._mm_to_motor_steps(self.go_until_speed))

    def release_switch(self):
        if not super().is_switch_on():
            return
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode
        super().release_switch(action=l6470.HOME_ACTION_CLEAR_ABS_POS,
                               direction=self.release_switch_direction)

    def home_shift(self):
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode
        super().set_max_speed(self._mm_to_motor_steps(self.go_until_speed))
        super().move(self._mm_to_micro_steps(self.home_shift_amount),
                     self.home_shift_direction)

    def position(self, position):
        super().set_max_speed(self._mm_to_motor_steps(self.pumping_speed))
        if position < self.top_pos:
            position = self.top_pos
        if position > self.bottom_pos:
            position = self.bottom_pos
        # start pumping motion
        # super().go_to(self._mm_to_micro_steps(position))
        if position > self.get_pos():
            super().go_to_dir(l6470.FWD, self._mm_to_micro_steps(position))
        else:
            super().go_to_dir(l6470.REV, self._mm_to_micro_steps(position))

    def volume(self, volume):
        super().set_max_speed(self._mm_to_motor_steps(self.pumping_speed))
        # calculate volume position
        volume_distance = self._volume_to_distance(volume)
        position = self.bottom_pos - volume_distance
        if position < self.top_pos:
            position = self.top_pos
        if position >= self.bottom_pos:
            position = self.bottom_pos
        # start pumping motion
        # super().go_to(self._mm_to_micro_steps(position))
        if position > self.get_pos():
            super().go_to_dir(l6470.FWD, self._mm_to_micro_steps(position))
        else:
            super().go_to_dir(l6470.REV, self._mm_to_micro_steps(position))

    def pumping(self, action, volume):
        # set speed
        if action == 'sup' or action == 'sdown':
            super().set_max_speed(self._mm_to_motor_steps(self.slow_pumping_speed))
        elif action == 'up' or action == 'down':
            super().set_max_speed(self._mm_to_motor_steps(self.pumping_speed))
        # calculate volume position
        volume_distance = self._volume_to_distance(volume)
        position = self.bottom_pos - volume_distance
        if position < self.top_pos:
            position = self.top_pos
        # start pumping motion
        # super().go_to(self._mm_to_micro_steps(position))
        if position > self.get_pos():
            super().go_to_dir(l6470.FWD, self._mm_to_micro_steps(position))
        else:
            super().go_to_dir(l6470.REV, self._mm_to_micro_steps(position))

    def stop(self):
        super().hard_stop()
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode

    def hard_stop(self):
        super().hard_stop()
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode

    def soft_stop(self):
        super().soft_stop()
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode

    def reset(self):
        super().reset_device()
        super().clear_status()
        self._init_params()
        super().set_switch_mode(l6470.CONFIG_SW_MODE_HARD_STOP)  # hard stop mode

    ###################################
    # init params
    ###################################
    '''
    mechanical considerations:
    - (+) direction is downwards and (-) direction is upwards
    - problem: home siwtch is paced at a too high position
    -- after go_until, (-) upwards 2 mm shift is needed to load the cartridge
       at this position, there is (-) 3 mm margin.
    -- home go_until: (-)
    '''
    def _init_params(self):
        # linear only
        self.lead = 1.0  # 1 mm / 1 rev
        # self.lead = 2.0  # 2 mm / 1 rev

        self.motor_steps_per_rev = 200
        super().set_step_mode(l6470.STEP_FS_128)
        self.micro_steps = super().get_micro_steps()
        self.micro_steps_per_rev = self.motor_steps_per_rev * self.micro_steps
        self.gear_ratio = 1.0

        self.max_speed = 5.0  # [mm/s], 5 mm in 1 s
        # self.max_speed = 3.0  # [mm/s], 5 mm in 1 s

        # [mm/s], considering any shock during start or stop
        self.min_speed = 1.0
        # self.min_speed = 0.7

        acc = self.max_speed * 10  # [mm/s/s], 0.1 s to max speed
        dec = acc
        super().set_max_speed(self._mm_to_motor_steps(self.max_speed))
        super().set_min_speed(self._mm_to_motor_steps(self.min_speed))
        super().set_acc(self._mm_to_motor_steps(acc))
        super().set_dec(self._mm_to_motor_steps(dec))

        super().set_stall_th(127) # max 127

        self.set_register(l6470.KVAL_ACC, 120)
        self.set_register(l6470.KVAL_DEC, 120)
        self.set_register(l6470.KVAL_RUN, 120)
        self.set_register(l6470.KVAL_HOLD, 20)

        # self.set_register(l6470.KVAL_ACC, 50)
        # self.set_register(l6470.KVAL_DEC, 50)
        # self.set_register(l6470.KVAL_RUN, 50)
        # self.set_register(l6470.KVAL_HOLD, 20)

        # Yun Duan Industrial linear actura
        # 0.6 A, 6.7 ohm -> 4.02 V -> 12 V with pwm ratio 85.425/255
        # self.set_register(l6470.KVAL_ACC, 128)
        # self.set_register(l6470.KVAL_ DEC, 128)
        # self.set_register(l6470.KVAL_RUN, 128)
        # self.set_register(l6470.KVAL_HOLD, 60)

        # 0.4 A, 11.5 ohm ->   V -> 12 V with pwm ratio  /255  # 8HY2062-01N 4.6VDC
        # self.set_register(l6470.KVAL_ACC, 64)
        # self.set_register(l6470.KVAL_DEC, 64)
        # self.set_register(l6470.KVAL_RUN, 64)
        # self.set_register(l6470.KVAL_HOLD, 20)
        
        # self.set_register(l6470.KVAL_ACC, 98)
        # self.set_register(l6470.KVAL_DEC, 98)
        # self.set_register(l6470.KVAL_RUN, 98)
        # self.set_register(l6470.KVAL_HOLD, 40)

        self.go_until_speed = 5.0  # [mm/s]
        self.go_until_direction = l6470.REV  # mechanically up
        self.release_switch_direction = l6470.FWD
        self.home_shift_direction = self.release_switch_direction
        # home relase switch speed = max(min speed or 5 motor-steps/s)
        # [mm], # shift after release switch to ensure that the switch is off enough
        # self.home_shift_amount = 0.5  # [mm]
        self.home_shift_amount = 0  # [mm]
        self.jog_speed = 5.0  # [mm/s]
        self.jog_amount = 3.0  # [mm]

        # mechanical properties
        # self.bottom_pos_def = 60.0  # 60.69 # [mm]
        self.bottom_pos_def = 45.0  # 60.69 # [mm]
        self.bottom_pos = self.bottom_pos_def
        self.top_pos = 0.0  # 28.00 # [mm]
        # self.up_offset = -1.75  # [mm]
        self.disk_radius = 3.0  # [mm]
        # pumping speed
        # self.pumping_speed = 6.25  # [mm/s], 6.25 rev/s
        self.pumping_speed = 5.0  # [mm/s], 3.0 rev/s
        self.slow_pumping_speed = 1.25  # [mm/s], 1.25 rev/s

    ###################################
    # bottom position
    ###################################
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
                self.bottom_pos = float(pos)
                # print(f'_load_bottom_pos, {self.bottom_pos}')
        except IOError:
            print('syringe bottom position load failed')
            self.bottom_pos = self.bottom_pos_def
            print(f'syringe bottom position set with default value {self.bottom_pos}')

    ###################################
    # volume to distance conversion
    ###################################
    def _volume_to_distance(self, volume):
        # convert volume to distance in mm
        volume_distance = volume / \
            (math.pi * self.disk_radius * self.disk_radius)
        return volume_distance

    ###################################
    # uint conversion
    ###################################

    def _micro_steps_to_mm(self, micro_steps):
        return (micro_steps/self.micro_steps_per_rev) * self.lead

    def _mm_to_micro_steps(self, mm):
        return mm / self.lead * self.micro_steps_per_rev

    def _mm_to_motor_steps(self, mm):
        return mm / self.lead * self.motor_steps_per_rev

    def _motor_steps_to_mm(self, motor_steps):
        return motor_steps / self.motor_steps_per_rev * self.lead


# syringe.py
