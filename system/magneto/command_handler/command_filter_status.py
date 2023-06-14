# -*- coding: utf-8 -*-
###############################################################################
# command_filter_status.py
###############################################################################
# import magneto.actuators.l6470 as l6470
from magneto.actuators.hardware_config import filter


#######################################
# get chamber status
#######################################
def check(command):
    return True, None, None

def start(command):
    running = filter.is_busy()
    driver_position = filter.get_pos()
    encoder_position = 0
    velocity = filter.get_velocity()
    registers = filter.get_registers()
    # print(registers)
    data = {'running': running, 'driver_position': driver_position, 'encoder_position': encoder_position, 'velocity': velocity, 'registers': registers}
    return (True, None, data)

def wait(command):
    return False

def stop(command):
    return (True, None, None)

# command_filter_status.py
