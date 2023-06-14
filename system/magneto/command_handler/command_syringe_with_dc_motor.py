# -*- coding: utf-8 -*-
###############################################################################
# command_syringe.py
###############################################################################
# from actuators.syringe_emulator import SyringeEmulator
# syringe = SyringeEmulator()
from actuators.syringe import Syringe
syringe = Syringe()


# 'syringe home'
# 'syringe stop'
# 'syringe position {mm} {speed}', speed: none, 'slow'(default), 'fast'
# 'syringe volume {volume} {speed}', speed: none, 'slow'(default), 'fast'
def _check_syringe_position(command):
    if len(command) < 3:
        return False, f'syringe position is required.'
    position = command[2]
    try:
        position = float(position)
    except ValueError:
        return False, f'syringe position "{position}" must be integer or float.'
    if position < 0:
        return False, f'syringe position must be positive.'
    return True, ''


def _check_syringe_volume(command):
    if len(command) < 3:
        return False, f'syringe volume is required.'
    volume = command[2]
    try:
        volume = float(volume)
    except ValueError:
        return False, f'syringe volume "{volume}" must be integer or float.'
    if volume < 0:
        return False, f'syringe volume must be positive.'
    return True, ''


def check_syringe(command):
    cmd = command[0]
    if len(command) < 2:
        return False, f'syringe action is required.'
    action = command[1]
    actions = ['home', 'stop', 'position', 'volume']
    if not action in actions:
        return False, f'syringe action "{action}" not correct'
    if action == 'home':
        return True, ''
    if action == 'stop':
        return True, ''
    if action == 'position':
        return _check_syringe_position(command)
    if action == 'volume':
        return _check_syringe_volume(command)
    print('internal error - invalid action in check_syringe()')


def start_syringe(command):
    cmd = command[0]
    action = command[1]
    print(action)
    if action == 'home':
        syringe.home()
    elif action == 'stop':
        syringe.stop()
    elif action == 'position':
        position = float(command[2])
        syringe.position(position)
    elif action == 'volume':
        volume = float(command[2])
        syringe.volume(volume)
    else:
        print('internal error - invalid action in start_syringe()')


def wait_syringe(command):
    return syringe.wait()


def stop_syringe(command):
    syringe.stop()


def home_syringe(command):
    syringe.home()


# command_syringe.py
