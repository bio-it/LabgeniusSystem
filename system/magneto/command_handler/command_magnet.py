# -*- coding: utf-8 -*-
###############################################################################
# command_magnet.py
###############################################################################
from magneto.actuators.hardware_config import magnet


def check(command):
    command = command.split()
    if len(command) < 2:
        return False, f'magnet action is required.', None

    cmd = command[0]
    action = command[1]
    actions = ['on', 'off', 'home']
    if not action in actions:
        return False, f'magnet action "{action}" not correct', None
    return True, None, None


def start(command):
    command = command.split()
    cmd = command[0]
    action = command[1]
    actions = ['on', 'off', 'home']
    if action == 'on':
        magnet.on()
        return True, None, None
    if action == 'off':
        magnet.off()
        return True, None, None
    if action == 'home':
        magnet.home()
        return True, None, None
    print('internal error - invalid action ({action}) in start_magnet()')
    return (False, 'internal error - invalid action ({action}) in start_magnet()', None)


def wait(command):
    return magnet.wait()


def stop(command):
    magnet.stop()
    return True, None, None

# command_magnet.py
