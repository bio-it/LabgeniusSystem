# -*- coding: utf-8 -*-
###############################################################################
# command_syringe_status.py
###############################################################################
# import magneto.actuators.l6470 as l6470
from magneto.actuators.hardware_config import syringe


#######################################
# get syringe status
#######################################
def check(command):
    return True, None, None

def start(command):
    running = syringe.is_busy()
    driver_position = syringe.get_pos()
    encoder_position = syringe.get_encoder_position()
    velocity = syringe.get_velocity()
    registers = syringe.get_registers()
    data = {'running': running, 'driver_position': driver_position, 'encoder_position': encoder_position, 'velocity': velocity, 'registers': registers}
    return (True, None, data)

def wait(command):
    return False

def stop(command):
    return (True, None, None)

# command_syringe_status.py
