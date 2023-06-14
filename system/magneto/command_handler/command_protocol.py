# -*- coding: utf-8 -*-
###############################################################################
# command_protocol.py
###############################################################################
import magneto.command_handler.command_home as command_home
import magneto.command_handler.command_magnet as command_magnet
import magneto.command_handler.command_chamber as command_chamber
import magneto.command_handler.command_syringe as command_syringe
import magneto.command_handler.command_waiting as command_waiting

# 'protocol home\nmagnet off\ngoto 11\npumping down full\npumping up 900\npumping sup 900\npumping sdown full\nmagnet on\npumping sdown 300\nwaiting 90'
_protocol_command_list = []
_protocol_command_list_index = -1

def check(command):
    command_raw = command  # 'protocol home\nmagnet off...'

    command = command.split()  # 'protocol', 'home', 'magnet', 'off'
    if len(command) == 1:
        return False, f'empty protocol', None

    first_word = command_raw.split()[0]  # 'protocol' or 'protocol_check'
    protocol = command_raw.replace(first_word, '')  # ' home\nmagnet off...'

    lines = protocol.split('\n')  # ' home', 'magnet off'

    global _protocol_command_list
    global _protocol_command_list_index
    _protocol_command_list = []
    _protocol_command_list_index = -1

    for i in range(0, len(lines)):
        line = lines[i]
        line = line.strip()
        command = line.split()
        cmd = command[0]
        if cmd == 'home':
            result, reason, data = command_home.check(line)
            if not result:
                return False, f'(line:{i+1}): "{reason}"', None
            _protocol_command_list.append(line)
        elif cmd == 'magnet':
            result, reason, data = command_magnet.check(line)
            if not result:
                return False, f'(line:{i+1}): "{reason}"', None
            _protocol_command_list.append(line)
        elif cmd == 'goto':
            result, reason, data = command_chamber.check('chamber ' + line)
            if not result:
                return False, f'(line:{i+1}): "{reason}"', None
            _protocol_command_list.append(line)
        elif cmd == 'pumping':
            result, reason, data = command_syringe.check('syringe ' + line)
            if not result:
                return False, f'(line:{i+1}): "{reason}"', None
            _protocol_command_list.append(line)
        elif cmd == 'waiting':
            result, reason, data = command_waiting.check(line)
            if not result:
                return False, f'(line:{i+1}): "{reason}"', None
            _protocol_command_list.append(line)
        else:
            _protocol_command_list = []
            _protocol_command_list_index = -1
            return False, f'(line:{i+1}) invlaid protocol command "{cmd}"', None
    # print(_protocol_command_list)
    return True, None, None


def _start_listed_command(command):
    splitted_command = command.split()
    cmd = splitted_command[0]
    if cmd == 'home':
        command_home.start(command)
    elif cmd == 'magnet':
        command_magnet.start(command)
    elif cmd == 'goto':
        command_chamber.start('chamber ' + command)
    elif cmd == 'pumping':
        command_syringe.start('syringe ' + command)
    elif cmd == 'waiting':
        command_waiting.start(command)
    else:
        print(f'internal error in _start_listed_command()')

def start(command):
    global _protocol_command_list_index
    _protocol_command_list_index = 0

    if len(_protocol_command_list) == 0:
        return True, None, None

    command = _protocol_command_list[_protocol_command_list_index]
    _start_listed_command(command)
    return True, None, None

    
def wait(command):
    global _protocol_command_list_index

    if len(_protocol_command_list) == 0:
        return False  # not waiting

    command = _protocol_command_list[_protocol_command_list_index]
    splitted_command = command.split()
    cmd = splitted_command[0]

    waiting = True
    if cmd == 'home':
        waiting = command_home.wait(command)
    elif cmd == 'magnet':
        waiting = command_magnet.wait(command)
    elif cmd == 'goto':
        waiting = command_chamber.wait('chamber ' + command)
    elif cmd == 'pumping':
        waiting = command_syringe.wait('syringe ' + command)
    elif cmd == 'waiting':
        waiting = command_waiting.wait(command)
    else:
        print(f'internal error in wait_porotocol()')

    if waiting:
        return True  # waiting

    # not waiting, go to next command
    _protocol_command_list_index += 1
    # check if all done
    if _protocol_command_list_index >= len(_protocol_command_list):
        _protocol_command_list_index = -1
        return False  # not waiting
    # call next start function
    command = _protocol_command_list[_protocol_command_list_index]
    _start_listed_command(command)
    return True  # waiting


def stop(command):
    print('stop_protocol({command})')
    global _protocol_command_list_index
    # get command
    if len(_protocol_command_list) == 0:
        return

    command = _protocol_command_list[_protocol_command_list_index]
    splitted_command = command.split()
    cmd = splitted_command[0]

    if cmd == 'home':
        command_home.stop(command)
    elif cmd == 'magnet':
        command_magnet.stop(command)
    elif cmd == 'goto':
        command_chamber.stop('chamber ' + command)
    elif cmd == 'pumping':
        command_syringe.stop('syringe ' + command)
    elif cmd == 'waiting':
        command_waiting.stop(command)
    else:
        print(f'internal error in stop_porotocol()')

    # clear index
    _protocol_command_list_index = -1
    return True, None, None


def dir(command):
    if len(_protocol_command_list) == 0:
        return ''
    if _protocol_command_list_index < 0:
        return ''
    command = _protocol_command_list[_protocol_command_list_index]
    # return command
    return f'{_protocol_command_list_index+1}/{len(_protocol_command_list)} : {command}'


def check_check(command):
    return check(command)
def check_start(command):
    return (True, None, None)
def check_wait(command):
    return False # no waiting
def check_stop(command):
    return (True, None, None)
def check_dir(command):
    return command
