# -*- coding: utf-8 -*-
###############################################################################
# command_filter.py
###############################################################################
from magneto.actuators.hardware_config import filter


# syringe home internal command list
_home_command_list = [
    'filter go_until',
    'filter release_switch',
    'filter home_shift',
]
_home_command_list_index = -1


def _start_filter_home():
    global _home_command_list_index
    print(f'{_home_command_list_index}')
    _home_command_list_index = 0
    command = _home_command_list[_home_command_list_index]
    print(f'_start_filter_home({command})')
    start(command)


def _wait_filter_home():
    global _home_command_list_index
    command = _home_command_list[_home_command_list_index]
    # print(f'_wait_filter_home({command})')
    # call wait function
    waiting = wait(command)
    # check waiting
    if waiting:
        return True  # waiting
    # not waiting, go to next command
    # print(f'_wait_filter_home()...wait done')
    _home_command_list_index += 1
    # check if all done
    if _home_command_list_index >= len(_home_command_list):
        _home_command_list_index = -1
        return False  # not waiting
    # call next start function
    command = _home_command_list[_home_command_list_index]
    start(command)
    return True  # waiting


def _stop_filter_home():
    global _protocol_command_list_index
    _home_command_list_index = -1
    filter.stop()


def check(command):
    '''
    'filter home'
    'filter go_until'
    'filter release_switch'
    'filter home_shift'
    'filter position'
    'filter goto'
    'filter jog + 10'
    '''
    # check action is given
    command = command.split()
    if len(command) < 2:  # check action is given
        return False, f'filter action is required.', None
    action = command[1]

    # check each action
    if action == 'home':
        return True, None, None
    if action == 'go_until':
        return True, None, None
    if action == 'release_switch':
        return True, None, None
    if action == 'home_shift':
        return True, None, None
    if action == 'position':
        if len(command) < 3:
            return False, f'filter position is required.', None
        position = command[2]
        try:
            position = float(position)
        except ValueError:
            return False, f'filter position ({position}) must be integer or float.', None
        if position < 0:
            return False, f'filter position must be positive.', None
        return True, None, None
    if action == 'goto':
        if len(command) < 3:
            return False, f'filter goto no is required.', None
        no = command[2]
        try:
            no = int(no)
        except ValueError:
            return False, f'filter no ({no}) must be integer.', None
        if no < filter.get_min_filter_no() or no > filter.get_max_filter_no():
            return False, f'filter number ({no}) is out of range', None
        return True, None, None
    if action == 'jog':    # [0]filter [1]jog [2]+/- [3]shift (optional)
        if len(command) < 3:
            return False, f'filter jog direction required', None
        direction = command[2]
        directions = ['+', '-']
        if not direction in directions:
            return False, f'filter direction ({direction}) not correct', None
        if len(command) >= 4:    # check jog shift
            shift = command[3]
            try:
                shift = float(shift)
            except ValueError:
                return False, f'filter jog shift  ({shift}) must be integer or float.', None
        return True, None, None
    if action == 'get_position':
        return True, None, None
    print('internal error - invalid action ({action}) in check_filter()')
    return False, f'invalid filter action ({action})', None


def start(command):
    command = command.split()
    action = command[1]
    if action == 'home':
        _start_filter_home()
        return (True, None, None)
    if action == 'go_until':
        filter.go_until()
        return (True, None, None)
    if action == 'release_switch':
        filter.release_switch()
        return (True, None, None)
    if action == 'home_shift':
        filter.home_shift()
        return (True, None, None)
    if action == 'position':
        position = command[2]
        position = float(position)
        filter.position(position)
        return (True, None, None)
    if action == 'goto':
        no = command[2]
        no = int(no)
        filter.goto(no)
        return (True, None, None)
    if action == 'jog':
        direction = command[2]
        shift = None
        if len(command) == 4:  # has jog shift
            shift = command[3]
            shift = float(shift)
        filter.jog(direction, shift)
        return (True, None, None)
    if action == 'get_position':
        driver_pos = filter.get_pos()
        end_pos = 0
        return (True, None, {'driver_pos': driver_pos, 'enc_pos': end_pos})
    print('internal error - invalid action ({action}) in start_filter()')
    return (False, 'internal error - invalid action ({action}) in start_filter()', None)


def wait(command):
    # return filter.wait()
    command = command.split()
    action = command[1]
    if action == 'home':
        return _wait_filter_home()
    else:
        return filter.wait()


def stop(command):
    # filter.stop()
    command = command.split()
    action = command[1]
    if action == 'home':
        return _stop_filter_home()
    else:
        filter.stop()
    return (True, None, None)


# command_filter.py
