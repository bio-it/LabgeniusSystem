# -*- coding: utf-8 -*-
###############################################################################
# command_home.py
###############################################################################
from magneto.actuators.hardware_config import filter
from magneto.actuators.hardware_config import magnet
from magneto.actuators.hardware_config import syringe
from magneto.actuators.hardware_config import chamber


class Command():
    def __init__(self, start_func, wait_func, stop_func):
        self.start_func = start_func
        self.wait_func = wait_func
        self.stop_func = stop_func

    def __str__(self):
        return f'CommandHome: {self.start_func}, {self.wait_func}, {self.stop_func}'

_command_list = [
    Command(filter.go_until, filter.wait, filter.stop),
    Command(filter.release_switch, filter.wait, filter.stop),
    Command(filter.home_shift, filter.wait, filter.stop),
    Command(magnet.home, magnet.wait, magnet.stop),
    Command(syringe.go_until, syringe.wait, syringe.stop),
    Command(syringe.release_switch, syringe.wait, syringe.stop),
    Command(syringe.set_encoder_zero_position, syringe.wait, syringe.stop),
    Command(syringe.home_shift, syringe.wait, syringe.stop),
    # Command(chamber.goto_home, chamber.wait, chamber.stop),
    Command(chamber.sync_with_encoder_position, chamber.wait, chamber.stop),
    Command(chamber.goto_home, chamber.wait, chamber.stop),
]  # _command_list
_command_list_index = -1


def check(command):
    return True, None, None


def start(command):
    global _command_list_index
    _command_list_index = 0
    _command_list[_command_list_index].start_func()
    return True, None, None


def wait(command):
    global _command_list_index
    # call wait function
    waiting = _command_list[_command_list_index].wait_func()
    # check waiting
    if waiting:
        return waiting
    # next command
    _command_list_index += 1
    # check all done
    if _command_list_index >= len(_command_list):
        _command_list_index = -1
        return False  # not waiting
    # call next start function
    _command_list[_command_list_index].start_func()
    return True  # waiting


def stop(command):
    global _command_list_index
    # check list index
    if _command_list_index < 0:
        return
    if _command_list_index >= len(_command_list):
        return
    # call stop function
    _command_list[_command_list_index].stop_func()
    # clear list index
    _command_list_index = -1
    return True, None, None

# command_home.py
