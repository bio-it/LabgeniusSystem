# -*- coding: utf-8 -*-
###############################################################################
# command_chamber.py
###############################################################################
from magneto.actuators.hardware_config import chamber

# chamber home internal command list
_home_command_list = [
  'chamber search_encoder_n_signal',
  'chamber go_to_encoder_n_signal',
  'chamber go_to_offset_position',
  'chamber set_home_position',
  'chamber shift_from_home',
  'chamber finish_home'
]
_home_command_list_index = -1


def _start_chamber_home():
    global _home_command_list_index
    _home_command_list_index = 0
    command = _home_command_list[_home_command_list_index]
    print(f'_start_chamber_home({command})')
    start(command)


def _wait_chamber_home():
    global _home_command_list_index
    command = _home_command_list[_home_command_list_index]
    # print(f'_wait_chamber_home({command})')
    # call wait function
    waiting = wait(command)
    # check waiting
    if waiting:
        return True  # waiting
    # not waiting, go to next command
    # print(f'_wait_chamber_home()...wait done')
    _home_command_list_index += 1
    # check if all done
    if _home_command_list_index >= len(_home_command_list):
        _home_command_list_index = -1
        return False  # not waiting
    # call next start function
    command = _home_command_list[_home_command_list_index]
    start(command)
    return True  # waiting


def _stop_chamber_home():
    global _protocol_command_list_index
    _home_command_list_index = -1
    chamber.stop()


def check(command):
  # check action is given
  command = command.split()
  if len(command) < 2:
    return False, f'chamber action is required.', None

  # check each action
  action = command[1]
  if action == 'home':
      return True, None, None
  if action == 'goto':
    if len(command) < 3:
      return False, f'chamber goto no is required.', None
    no = command[2]
    try:
      no = int(no)
    except ValueError:
      return False, f'chamber no ({no}) must be integer.', None
    if no < chamber.get_min_chamber_no() or no > chamber.get_max_chamber_no():
      return False, f'chamber number ({no}) is out of range', None
    return True, None, None
  if action == 'position':
    if len(command) < 3:
      return False, f'chamber position is required.', None
    position = command[2]
    try:
      position = float(position)
    except ValueError:
      return False, f'chamber position ({position}) must be integer or float.', None
    # if position < 0:
    #   return False, f'chamber position must be positive.', None
    return True, None, None
  if action == 'jog':    # [0]chamber [1]jog [2]+/- [3]shift (optional)
    if len(command) < 3:
        return False, f'chamber jog direction required', None
    direction = command[2]
    directions = ['+', '-']
    if not direction in directions:
        return False, f'chamber direction ({direction}) not correct', None
    if len(command) >= 4:    # check jog shift
      shift = command[3]
      try:
        shift = float(shift)
      except ValueError:
        return False, f'chamber jog shift  ({shift}) must be integer or float.', None
    return True, None, None
  if action == 'get_position':
      return True, None, None
  if action == 'set_encoder_zero_position':
      return True, None, None
  if action == 'sync_with_encoder_position':
      return True, None, None
  if action == 'goto_home':
      return True, None, None
  if action == 'search_encoder_n_signal':
      return True, None, None
  if action == 'go_to_encoder_n_signal':
      return True, None, None
  if action == 'go_to_offset_position':
      return True, None, None
  if action == 'set_home_position':
      return True, None, None
  if action == 'shift_from_home':
      return True, None, None
  if action == 'finish_home':
      return True, None, None
  if action == 'save_offset_position':
      return True, None, None
  print(f'internal error - invalid action ({action}) in check_chamber()')
  return False, f'invalid chamber action ({action})', None



def start(command):
  command = command.split()
  action = command[1]
  if action == 'home':
    _start_chamber_home()
    return (True, None, None)
  if action == 'goto':
    no = command[2]
    no = int(no)
    chamber.goto(no)
    return (True, None, None)
  if action == 'position':
    position = command[2]
    position = float(position)
    chamber.position(position)
    return (True, None, None)
  if action == 'jog':
    direction = command[2]
    shift = None
    if len(command) == 4:  # has jog shift
      shift = command[3]
      shift = float(shift)
      chamber.jog(direction, shift)
      return (True, None, None)
  if action == 'get_position':
    driver_pos = chamber.get_pos()
    end_pos = chamber.get_enc_pos()
    return (True, None, {'driver_pos': driver_pos, 'enc_pos': end_pos})
  if action == 'set_encoder_zero_position':
    chamber.set_encoder_zero_position()
    chamber.set_pos(0)
    return (True, None, None)
  if action == 'sync_with_encoder_position':
    chamber.sync_with_encoder_position()
    return (True, None, None)
  if action == 'goto_home':
    chamber.goto_home()
    return (True, None, None)
  if action == 'search_encoder_n_signal':
    chamber.search_encoder_n_signal()
    return (True, None, None)
  if action == 'go_to_encoder_n_signal':
    chamber.go_to_encoder_n_signal()
    return (True, None, None)
  if action == 'go_to_offset_position':
    chamber.go_to_offset_position()
    return (True, None, None)
  if action == 'set_home_position':
    chamber.set_home_position()
    return (True, None, None)
  if action == 'shift_from_home':
    chamber.shift_from_home()
    return (True, None, None)
  if action == 'finish_home':
    chamber.finish_home()
    return (True, None, None)
  if action == 'save_offset_position':
    chamber.save_offset_position()
    return (True, None, None)
  print(f'internal error - invalid action ({action}) in start_chamber()')
  return (False, 'internal error - invalid action ({action}) in start_chamber()', None)


def wait(command):
  command = command.split()
  action = command[1]
  if action == 'home':
    return _wait_chamber_home()
  else:
    return chamber.wait()


def stop(command):
  command = command.split()
  action = command[1]
  if action == 'home':
    return _stop_chamber_home()
  else:
    chamber.stop()
  return (True, None, None)

# command_chamber.py
