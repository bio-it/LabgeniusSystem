# -*- coding: utf-8 -*-
###############################################################################
# command_pumping.py
###############################################################################
from magneto.actuators.hardware_config import syringe


def check(command):
    command = command.split()
    # check direction
    if len(command) < 2:
        return False, f'syringe pumping direction is required.', None
    direction = command[1]
    directions = ['down', 'sdown', 'up', 'sup']
    if not direction in directions:
        return False, f'syringe pumping direction ({direction}) is not correct', None
    # check volume
    if len(command) < 3:
        return False, f'syringe pumping volume is required.', None
    volume = command[2]
    if volume == 'full':
        volume = '0'
    try:
        volume = float(volume)
    except ValueError:
        return False, f'syringe pumping volume ({volume}) must be integer, float, or "full".', None
    if volume < 0:
        return False, f'syringe volume must be positive or "full".', None
    return True, None, None


def start(command):
    command = command.split()
    direction = command[1]
    volume = command[2]
    if volume == 'full':
        volume = '0'
    volume = float(volume)
    syringe.pumping(direction, volume)
    return (True, None, None)


def wait(command):
    return syringe.wait()


def stop(command):
    syringe.stop()
    return (True, None, None)

# command_pumping.py
