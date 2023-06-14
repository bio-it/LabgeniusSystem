# -*- coding: utf-8 -*-
###############################################################################
# command_chamber_status.py
###############################################################################
# import magneto.actuators.l6470 as l6470
from magneto.actuators.hardware_config import chamber


#######################################
# get chamber status
#######################################
def check(command):
    return True, None, None

def start(command):
    running = chamber.is_busy()
    driver_position = chamber.get_pos()
    encoder_position = chamber.get_encoder_position()
    velocity = chamber.get_velocity()
    registers = chamber.get_registers()
    data = {'running': running, 'driver_position': driver_position, 'encoder_position': encoder_position, 'velocity': velocity, 'registers': registers}
    return (True, None, data)

def wait(command):
    return False

def stop(command):
    return (True, None, None)

# command_chamber_status.py
