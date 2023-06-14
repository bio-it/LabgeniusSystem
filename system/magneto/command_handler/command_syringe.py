# -*- coding: utf-8 -*-
###############################################################################
# command_syringe.py
###############################################################################
from magneto.actuators.hardware_config import syringe


# syringe home internal command list
_home_command_list = [
  'syringe release_switch',
  'syringe search_switch',
  'syringe go_to_switch_latch_position',
  'syringe search_encoder_n_signal',
  'syringe go_to_encoder_n_signal',
  'syringe set_home_position',
  'syringe shift_from_home',
  'syringe finish_home'
]
_home_command_list_index = -1


def _start_syringe_home():
  global _home_command_list_index
  _home_command_list_index = 0
  command = _home_command_list[_home_command_list_index]
  print(f'_start_syringe_home({command})')
  start(command)


def _wait_syringe_home():
  global _home_command_list_index
  command = _home_command_list[_home_command_list_index]
  # print(f'_wait_syringe_home({command})')
  # call wait function
  waiting = wait(command)
  # check waiting
  if waiting:
    return True  # waiting
  # not waiting, go to next command
  # print(f'_wait_syringe_home()...wait done')
  _home_command_list_index += 1
  # check if all done
  if _home_command_list_index >= len(_home_command_list):
    _home_command_list_index = -1
    return False  # not waiting
  # call next start function
  command = _home_command_list[_home_command_list_index]
  start(command)
  return True  # waiting


def _stop_syringe_home():
  global _protocol_command_list_index
  _home_command_list_index = -1
  syringe.stop()


def check(command):
  '''
  'syringe', 'go_until'
  'syringe', 'release_switch'
  'syringe', 'home_shift'
  'syringe', 'position', '20'
  'syringe', 'volume', '100'
  'syringe', 'pumping down', 'full'
  'syringe', 'pumping sdown', 'full'
  'syringe', 'pumping sdown', '300'
  'syringe', 'pumping up', '900'
  'syringe', 'pumping sup', '900'
  'syringe', 'get_position'
  'syringe', 'save_bottom_position'
  '''
  # check action is given
  command = command.split()
  if len(command) < 2:
    return False, f'syringe action is required.', None

  # check action is given
  action = command[1]

  if action == 'home':
    return True, None, None
  if action == 'release_switch':
    return True, None, None
  if action == 'search_switch':
    return True, None, None
  if action == 'go_to_switch_latch_position':
    return True, None, None
  if action == 'search_encoder_n_signal':
      return True, None, None
  if action == 'go_to_encoder_n_signal':
      return True, None, None
  if action == 'set_home_position':
    return True, None, None
  if action == 'shift_from_home':
    return True, None, None
  if action == 'finish_home':
    return True, None, None
  if action == 'save_bottom_position':
    return True, None, None

  if action == 'position':
    if len(command) < 3:
      return False, f'syringe position is required.', None
    position = command[2]
    try:
      position = float(position)
    except ValueError:
      return False, f'syringe position ({position}) must be integer or float.', None
    if position < 0:
      return False, f'syringe position must be positive.', None
    return True, None, None
  if action == 'jog':    # [0]syringe [1]jog [2]+/- [3]shift (optional)
    if len(command) < 3:
      return False, f'syringe jog direction required', None
    direction = command[2]
    directions = ['+', '-']
    if not direction in directions:
      return False, f'syringe direction ({direction}) not correct', None
    if len(command) >= 4:    # check jog shift
      shift = command[3]
      try:
        shift = float(shift)
      except ValueError:
        return False, f'syringe jog shift  ({shift}) must be integer or float.', None
    return True, None, None
  if action == 'volume':
    if len(command) < 3:
      return False, f'syringe volume is value required.', None
    volume = command[2]
    try:
      volume = float(volume)
    except ValueError:
      return False, f'syringe volume ({volume}) must be integer or float.', None
    if volume < 0:
      return False, f'syringe volume must be positive.', None
    return True, None, None
  if action == 'pumping':
    # check direction
    if len(command) < 3:
      return False, f'syringe pumping direction is required.', None
    direction = command[2]
    directions = ['down', 'sdown', 'up', 'sup']
    if not direction in directions:
      return False, f'syringe pumping direction ({direction}) is not correct', None
    # check volume
    if len(command) < 4:
      return False, f'syringe pumping volume is required.', None
    volume = command[3]
    if volume == 'full':
      volume = '0'
    try:
      volume = float(volume)
    except ValueError:
      return False, f'syringe pumping volume ({volume}) must be integer, float, or "full".', None
    if volume < 0:
      return False, f'syringe volume must be positive or "full".', None
    return True, None, None
  if action == 'get_position':
    return True, None, None
  # if action == 'set_encoder_zero_position':
  #     return True, None, None
  print(f'internal error - invalid action ({action}) in check_syringe()')
  return False, f'invalid syringe action ({action})', None


def start(command):
  command = command.split()
  action = command[1]

  if action == 'home':
      _start_syringe_home()
      return (True, None, None)
  if action == 'release_switch':
    syringe.release_switch()
    return (True, None, None)
  if action == 'search_switch':
    syringe.search_switch()
    return (True, None, None)
  if action == 'go_to_switch_latch_position':
    syringe.go_to_switch_latch_position()
    return (True, None, None)
  if action == 'search_encoder_n_signal':
    syringe.search_encoder_n_signal()
    return (True, None, None)
  if action == 'go_to_encoder_n_signal':
    syringe.go_to_encoder_n_signal()
    return (True, None, None)
  if action == 'set_home_position':
    syringe.set_home_position()
    return (True, None, None)
  if action == 'shift_from_home':
    syringe.shift_from_home()
    return (True, None, None)
  if action == 'finish_home':
    syringe.finish_home()
    return (True, None, None)
  # if action == 'set_encoder_zero_position':
  #   syringe.set_encoder_zero_position()
  #   return (True, None, None)
  if action == 'save_bottom_position':
    syringe.save_bottom_position()
    return (True, None, None)

  if action == 'position':
    position = command[2]
    position = float(position)
    syringe.position(position)
    return (True, None, None)
  if action == 'jog':
    direction = command[2]
    shift = None
    if len(command) == 4:  # has jog shift
      shift = command[3]
      shift = float(shift)
    syringe.jog(direction, shift)
    return (True, None, None)
  if action == 'volume':
    volume = command[2]
    volume = float(volume)
    syringe.volume(volume)
    return (True, None, None)
  if action == 'pumping':
    direction = command[2]
    volume = command[3]
    if volume == 'full':
      volume = '0'
    volume = float(volume)
    syringe.pumping(direction, volume)
    return (True, None, None)
  if action == 'get_position':
    driver_pos = syringe.get_pos()
    end_pos = syringe.get_enc_pos()
    return (True, None, {'driver_pos': driver_pos, 'enc_pos': end_pos})
  print(f'internal error - invalid action ({action}) in start_syringe()')
  return (False, f'internal error - invalid action ({action}) in start_syringe()', None)


def wait(command):
  # return syringe.wait()
  command = command.split()
  action = command[1]
  if action == 'home':
    return _wait_syringe_home()
  else:
    return syringe.wait()


def stop(command):
  # syringe.stop()
  command = command.split()
  action = command[1]
  if action == 'home':
    return _stop_syringe_home()
  else:
    syringe.stop()
  return (True, None, None)


# command_syringe.py
