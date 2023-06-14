# -*- coding: utf-8 -*-
###############################################################################
# command_handler.py
###############################################################################
import magneto.command_handler.command_chamber as command_chamber
import magneto.command_handler.command_syringe as command_syringe
import magneto.command_handler.command_magnet as command_magnet
import magneto.command_handler.command_filter as command_filter
import magneto.command_handler.command_home as command_home
import magneto.command_handler.command_waiting as command_waiting
import magneto.command_handler.command_goto as command_goto
import magneto.command_handler.command_pumping as command_pumping
import magneto.command_handler.command_print as command_print
import magneto.command_handler.command_protocol as command_protocol
import magneto.command_handler.command_chamber_status as command_chamber_status
import magneto.command_handler.command_syringe_status as command_syringe_status
import magneto.command_handler.command_filter_status as command_filter_status
import magneto.command_handler.command_magnet_status as command_magnet_status
from magneto.command_handler.command_registers import (
    check_set_register, start_set_register, wait_set_register, stop_set_register)
from magneto.actuators.hardware_config import chamber, syringe, filter, magnet

'''
check fucntion, start function, stop function returns (result True/False, reason string, data string)
wait function returns True for keeping waiting or False for fininishing
dir function return a string for running command
'''

#######################################
# command handler map
#######################################


def default_check(command):
    return True, None, None


def default_start(command):
    return True, None, None


def default_wait(command):
    return False


def default_stop(command):
    return True, None, None


def default_dir(command):
    return command


class Command():
    # command map element structure
    def __init__(self, name, instant, check_func, start_func, wait_func, stop_func, dir_func):
        self.name = name
        self.instant = instant
        self.check_func = check_func
        self.start_func = start_func
        self.wait_func = wait_func
        self.stop_func = stop_func
        self.dir_func = dir_func

    def __str__(self):
        return f'Command: {self.name}, {self.instant}, {self.check_func}, {self.start_func}, {self.wait_func}, {self.stop_func}, {self.dir_func}'


_commands = [
    # actuators
    Command('chamber', False, command_chamber.check, command_chamber.start,
            command_chamber.wait, command_chamber.stop, default_dir),
    Command('syringe', False, command_syringe.check, command_syringe.start,
            command_syringe.wait, command_syringe.stop, default_dir),
    Command('magnet', False, command_magnet.check, command_magnet.start,
            command_magnet.wait, command_magnet.stop, default_dir),
    Command('filter', False, command_filter.check, command_filter.start,
            command_filter.wait, command_filter.stop, default_dir),
    # protocol
    Command('ready', True, default_check, default_start,
            default_wait, default_stop, default_dir),
    Command('home', False, command_home.check, command_home.start,
            command_home.wait, command_home.stop, default_dir),
    Command('waiting', False, command_waiting.check, command_waiting.start,
            command_waiting.wait, command_waiting.stop, command_waiting.dir),
    Command('goto', False, command_goto.check, command_goto.start,
            command_goto.wait, command_goto.stop, default_dir),
    Command('pumping', False, command_pumping.check, command_pumping.start,
            command_pumping.wait, command_pumping.stop, default_dir),
    Command('print', False, command_print.check, command_print.start,
            command_print.wait, command_print.stop, command_print.dir),
    Command('protocol_run', False, command_protocol.check, command_protocol.start,
            command_protocol.wait, command_protocol.stop, command_protocol.dir),
    Command('protocol_check', True, command_protocol.check_check, command_protocol.check_start,
            command_protocol.check_wait, command_protocol.check_stop, command_protocol.check_dir),
    # get actuators status
    Command('get_chamber_status', True, command_chamber_status.check, command_chamber_status.start,
            command_chamber_status.wait, command_chamber_status.stop, default_dir),
    Command('get_syringe_status', True, command_syringe_status.check, command_syringe_status.start,
            command_syringe_status.wait, command_syringe_status.stop, default_dir),
    Command('get_filter_status', True, command_filter_status.check, command_filter_status.start,
            command_filter_status.wait, command_filter_status.stop, default_dir),
    Command('get_magnet_status', True, command_magnet_status.check, command_magnet_status.start,
            command_magnet_status.wait, command_magnet_status.stop, default_dir),
    # registers
    Command('set_register', True, check_set_register, start_set_register,
            wait_set_register, stop_set_register, default_dir),

]  # _commands
_commands_name_map = {c.name: c for c in _commands}


def check_command(command):
    # returns (result, reason, data)
    # print(f'check_command({command})')
    command_raw = command
    command = command.split()
    if len(command) == 0:
        return False, f'empty command', None
    cmd = command[0]
    if cmd in _commands_name_map:
        result, reason, data = _commands_name_map[cmd].check_func(command_raw)
        if result == False:
            return False, reason, None
        else:
            return True, None, None
    else:
        return False, f'invalid command: {cmd}', None


def is_instant(command):
    command = command.split()
    cmd = command[0]
    if cmd in _commands_name_map:
        return _commands_name_map[cmd].instant
    else:
        print(
            f'internal error in is_instant(), invalid internal command {cmd}')
        return False


def start_command(command):
    command_raw = command
    command = command.split()
    cmd = command[0]
    if cmd in _commands_name_map:
        # return(result, reason, data)
        return _commands_name_map[cmd].start_func(command_raw)
    else:
        print(
            f'internal error in start_command(), invalid internal command {cmd}')
        return False, f'internal error in start_command(), invalid internal command {cmd}', None


def wait_command(command):
    command_raw = command
    command = command.split()
    cmd = command[0]
    if cmd in _commands_name_map:
        return _commands_name_map[cmd].wait_func(command_raw)
    else:
        print(
            f'internal error in wait_command(), invalid internal command {cmd}')
        return True


def stop_command(command):
    print(f'stop_command({command})')
    command_raw = command
    command = command.split()
    cmd = command[0]
    # call stop function
    if cmd in _commands_name_map:
        return _commands_name_map[cmd].stop_func(command_raw)
    print(f'internal error in stop_command(), invalid internal command {cmd}')
    return False, f'internal error in start_command(), invalid internal commandd {cmd}', None


def dir_command(command):
    if command == '':
        return ''
    command_raw = command
    command = command.split()
    cmd = command[0]
    if cmd in _commands_name_map:
        return _commands_name_map[cmd].dir_func(command_raw)
    print(f'internal error in dir_command(), invalid internal command {cmd}')
    return f'internal error in dir_command(), invalid internal command {cmd}'


#######################################
# other functions
#######################################
def is_stop_command(command):
    command = command.split()
    cmd = command[0]
    if cmd == 'stop':
        return True
    else:
        return False


def stop():
    chamber.soft_stop()
    syringe.soft_stop()
    filter.soft_stop()
    chamber.clear_status()
    syringe.clear_status()
    filter.clear_status()
    magnet.stop()


def is_get_status_command(command):
    command = command.split()
    cmd = command[0]
    if cmd == 'get_status':
        return True
    else:
        return False


def get_print_message():
    return command_print.get_message()

# command_handler.py
