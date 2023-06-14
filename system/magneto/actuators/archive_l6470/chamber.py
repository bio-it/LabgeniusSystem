###############################################################################
# chamber.py
###############################################################################
import math
from time import sleep
import magneto.actuators.l6470 as l6470
from magneto.actuators.l6470_stepper import L6470Stepper
# from magneto.actuators.amt203 import AMT203
# encoder  = AMT203(3, 0)   # Abs.Encoder_AMT203-V, Device_3[CS_1]_(Optic.Filter) # self.spi = init_spi(0, 3, 0)
# # syringe_encoder = AMT203(4, 0) # Abs.Encoder_AMT203-V, Device_4[CS_2]_(Qwiic Pro Micro) # self.spi = init_spi(0, 4, 0)

###############################################################################
# Chamber class based on L6470 stepper
###############################################################################
class Chamber(L6470Stepper):
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
            print(f'Chamber driver not detected.')
            raise(SystemExit)
        self._init_params()
        print(f'Chamber initialized')

        # check encoder
        enc_pos, _ = self.encoder.read_abs_pos()
        if enc_pos == -1:
            print('Chamber abs encoder not detected')
            raise(SystemExit)
        print('Chamber abs encoder detected')
        
        # encoder multi-turn
        self.prev_encoder_count = self.encoder.get_pos()
        self.encoder_multi_turn_count = self.prev_encoder_count
        self.encoder_position = self.encoder_multi_turn_count * 360.0 / 4096

        # sync L6470 abs pos with abs encoder
        # print(f'chamber pos before sync:{super().get_pos()}')
        enc_pos = self.get_encoder_position()
        self.set_pos(enc_pos)
        # print(f'chamber pos after sync:{super().get_pos()}')
        # print(f'enc pos={self.get_encoder_position()}, pos={self.get_pos()}')


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
        # convert count to deg
        self.encoder_position = self.encoder_multi_turn_count * 360.0 / 4096

    def print_position(self):
        # print(f'{self.get_encoder_position()}, {self.get_pos()}')
        print(f'{self.get_encoder_position()}, {self.get_pos()}, {self.get_encoder_position()-self.get_pos()}')

    def print_encoder_position(self):
        print(f'{self.get_encoder_position()}')


    ###################################
    # interface functions
    ###################################
    def get_min_chamber_no(self):
        return self.min_chamber_no

    def get_max_chamber_no(self):
        return self.max_chamber_no

    def get_register(self, no):
        return super().get_register(no)

    def set_register(self, no, value):
        super().set_register(no, value)

    def get_pos(self):
        return self._micro_steps_to_deg(super().get_pos())
 
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
        super().set_max_speed(self._deg_to_motor_steps(self.jog_speed))
        super().move(self._deg_to_micro_steps(amount), direction)

    # def move(self, position):
    #     super().go_to(self._deg_to_micro_steps(position))

    def run(self, direction, motor_steps_per_sec):    # Run (DIR, SPD)
        super().run(direction=l6470.FWD,
                         motor_steps_per_sec=self._deg_to_motor_steps(motor_steps_per_sec))
                         

    def get_abs_pos(self):
        return self.encoder.read_abs_pos() * 360.0 / 4096.0

    def set_pos(self, pos):
        super().set_register(l6470.ABS_POS, self._deg_to_micro_steps(pos), signed=True)

    def goto_home(self):
        super().go_to(self._deg_to_micro_steps(self.home_pos))
        print(f'chamber home, enc pos={self.get_encoder_position()}, pos={self.get_pos()}')

    def sync_with_encoder_position(self):
        pos = self.get_encoder_position()
        self.set_pos(pos)
        print(f'chamber sync_with_encoder_position, enc pos={self.get_encoder_position()}, pos={self.get_pos()}')

    # def home_shift(self):
    #     super().go_to_dir(l6470.FWD, self._deg_to_micro_steps(self.home_pos+self.home_shift_amount))

    def set_driver_position_to_zero(self):
        super().reset_pos()


    def goto(self, no):
        # interval = 360 / self.max_chamber_no
        # position = interval * (no - 1)
        position = self._no_to_deggree(no)
        print(f'goto():{position}, {self._deg_to_micro_steps(position)}')
        super().set_max_speed(self._deg_to_motor_steps(self.goto_speed))
        super().go_to(self._deg_to_micro_steps(position))

    def _is_dir_change(self, position):
        cur_dir = True
        if position < self.get_pos():
            cur_dir = False
        if cur_dir != self.prev_dir:
            self.prev_dir = cur_dir
            return True
        else:
            return False

    def position(self, position):
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
        self._init_params()

    ###################################
    # init params
    ###################################
    def _init_params(self):
        self.motor_steps_per_rev = 200 # common step motor
        self.set_step_mode(l6470.STEP_FS_128)  # common step motor
        self.micro_steps = super().get_micro_steps()
        self.micro_steps_per_rev = self.motor_steps_per_rev * self.micro_steps
        self.gear_ratio = 1  # default
        self.home_pos = 0 # [deg] PG35S-D48-HHC2
        # self.home_pos = -55 # [deg] PG35S-D48-HHC2
        # self.home_shift_amount = 5 # [deg], backlash tracking
        # self.backlash = 1.4 # [deg] PG35S-D48-HHC2
        # self.prev_dir = True # positive, backlash tracking
        # self.prev_enc_pos = 0 # abs encoder tracking
        # self.turns = 0  # abs encoder tracking
       
        self.max_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
        self.min_speed = 10  # [deg/s], considering any shock during start or stop
        # self.min_speed = 1  # [deg/s], considering any shock during start or stop
        acc = self.max_speed * 10  # [deg/s/s], 0.1 s to max speed
        # acc = self.max_speed * 1  # [deg/s/s], 1 s to max speed
        dec = acc
        self.set_max_speed(self._deg_to_motor_steps(self.max_speed))
        self.set_min_speed(self._deg_to_motor_steps(self.min_speed))
        self.set_acc(self._deg_to_motor_steps(acc))
        self.set_dec(self._deg_to_motor_steps(dec))

        super().set_stall_th(127) # max 127

        self.set_register(l6470.KVAL_ACC, 90)     # NEMA17-19-07PD -->> STEP_LOSS_A STEP_LOSS_B
        self.set_register(l6470.KVAL_DEC, 90)
        self.set_register(l6470.KVAL_RUN, 90)
        self.set_register(l6470.KVAL_HOLD,20)

        # step loss
        # self.set_register(l6470.KVAL_ACC, 120)     # NEMA17-19-07PD -->> STEP_LOSS_A STEP_LOSS_B
        # self.set_register(l6470.KVAL_DEC, 120)
        # self.set_register(l6470.KVAL_RUN, 120)
        # self.set_register(l6470.KVAL_HOLD, 20)

        # self.set_register(l6470.KVAL_ACC, 180)    # NEMA17-19-07PD -->> ["OCD"] STEP_LOSS_B
        # self.set_register(l6470.KVAL_DEC, 180)
        # self.set_register(l6470.KVAL_RUN, 120)
        # self.set_register(l6470.KVAL_HOLD, 20)

        # ocd
        # self.set_register(l6470.KVAL_ACC, 200)
        # self.set_register(l6470.KVAL_DEC, 200)
        # self.set_register(l6470.KVAL_RUN, 200)
        # self.set_register(l6470.KVAL_HOLD,20)

        # self.go_until_speed = self.max_speed  # [deg/s]
        # self.go_until_direction = l6470.FWD
        # self.release_switch_direction = l6470.REV
        # self.home_shift_direction = self.release_switch_direction
        # home relase switch speed = max(min speed or 5 motor-steps/s)
        # [deg], # shift after release switch to ensure that the switch is off enough
        # self.home_shift_amount = 5 #[deg]
        self.jog_amount = 5  # [deg]
        self.jog_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
        # goto command
        self.min_chamber_no = 1
        self.max_chamber_no = 13
        # self.goto_speed = 360.0 / 2  # [deg/s], 360 deg in 2 s
        self.goto_speed = 360.0 * 2


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
        theta = 20.77
        ch_3_pos = 90.0 - theta
        chamber_no_diff = chamber_no - 3
        pos = chamber_no_diff * 360 / 13
        pos = pos + ch_3_pos
        if pos > 360.0:
            pos = pos - 360
        return pos

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


# chamber.py
