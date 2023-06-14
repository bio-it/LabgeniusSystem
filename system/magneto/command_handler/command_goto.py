# -*- coding: utf-8 -*-
###############################################################################
# command_goto.py
###############################################################################
from magneto.actuators.hardware_config import chamber


def check(command):
    command = command.split()
    if len(command) < 2:
        return False, f'chamber goto no is required.', None
    no = command[1]
    try:
        no = int(no)
    except ValueError:
        return False, f'chamber no ({no}) must be integer.', None
    if no < chamber.get_min_chamber_no() or no > chamber.get_max_chamber_no():
        return False, f'chamber number ({no}) is out of range', None
    return True, None, None


def start(command):
    command = command.split()
    no = command[1]
    no = int(no)
    chamber.goto(no)
    return (True, None, None)


def wait(command):
    return chamber.wait()


def stop(command):
    chamber.stop()
    return (True, None, None)

# command_goto.py
