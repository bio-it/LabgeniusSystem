# -*- coding: utf-8 -*-
###############################################################################
# command_waiting.py
###############################################################################
from time import time

_waiting_time = 0
_waiting_start_time = 0


def check(command):
    global _waiting_time, _waiting_start_time
    command = command.split()
    if len(command) < 2:
        return False, f'waiting time is required.', None
    waiting_time = command[1]
    try:
        waiting_time = float(waiting_time)
    except ValueError:
        return False, f'waiting time "{waiting_time}" must be integer or float.', None
    if waiting_time < 0:
        return False, f'waiting time must be positive.', None
    return True, None, None


def start(command):
    global _waiting_time, _waiting_start_time
    command = command.split()
    cmd = command[0]
    waiting_time = command[1]
    try:
        waiting_time = float(waiting_time)
    except ValueError:
        print(
            f'internal error in start_waiting() - waiting_time "{waiting_time}" must be integer or float.')
        return False, f'internal error in start_waiting() - waiting_time "{waiting_time}" must be integer or float.', None

    _waiting_time = waiting_time
    _waiting_start_time = time()
    return True, None, None


def wait(command):
    global _waiting_time, _waiting_start_time
    current_time = time()
    if current_time - _waiting_start_time >= _waiting_time:
        return False  # not waiting
    else:
        # print(f'wait waiting:{current_time - _waiting_start_time - _waiting_time}')
        return True  # still waiting


def stop(command):
    global _waiting_start_time
    _waiting_start_time = time()
    return True, None, None


def dir(command):
    remained_time = (_waiting_start_time + _waiting_time) - time()
    return f'{command} ({remained_time:.1f})'

# command_waiting.py
