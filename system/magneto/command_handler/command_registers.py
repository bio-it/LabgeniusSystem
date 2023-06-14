# -*- coding: utf-8 -*-
###############################################################################
# command_registers.py
###############################################################################
# import magneto.actuators.tmc5130 as tmc5130
import magneto.actuators.tmc5130 as tmc5130
from magneto.actuators.hardware_config import (chamber, syringe, filter)


def check_set_register(command):
    # 'set_register syringe config 0x2020'
    command = command.split()

    if len(command) < 2:
        return False, f'actuator is required.', None
    actuator = command[1]
    actuators = ['chamber', 'syringe', 'filter']
    if not actuator in actuators:
        return False, f'set_register actuator "{actuator}" not correct'

    if len(command) < 3:
        return False, f'register is required.', None
    register = command[2]
    register = tmc5130.name_to_no(register)
    if register == None:
        return False, f'set_register register "{register}" not correct'

    if len(command) < 4:
        return False, f'value is required.', None
    value = command[3]
    try:
        value = int(value, base=0) # base guessing
    except ValueError:
        return False, f'value ({value}) must be integer.', None
    
    return True, None, None


def start_set_register(command):
    # 'set_register syringe config 0x2020'
    command = command.split()
    actuator = command[1]
    register = command[2]
    register = tmc5130.name_to_no(register)
    value = command[3]
    value = int(value, base=0) # base guessing
    if actuator =='chamber':
        chamber.set_register(register, value)
    elif actuator =='syringe':
        syringe.set_register(register, value)
    elif actuator =='filter':
        filter.set_register(register, value)
    return True, None, None


def wait_set_register(command):
    return False

def stop_set_register(command):
    return (True, None, None)


# command_registers.py
