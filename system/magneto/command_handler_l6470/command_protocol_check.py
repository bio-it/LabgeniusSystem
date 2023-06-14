#######################################
# protocol command
#######################################
from magneto.command_handler import start_command, wait_command, stop_command
# 'protocol_check home\nmagnet off\ngoto 11\npumping down full\npumping up 900\npumping sup 900\npumping sdown full\nmagnet on\npumping sdown 300\nwaiting 90'
_protocol_command_list = []
_protocol_command_list_index = -1


def check_protocol_check(command):
    # print(f'check_protocol({command})')
    # get protocols
    command_raw = command  # 'protocol_check home\nmagnet off...'
    command = command.split()  # 'protocol_check', 'home\nmagnet', 'off', ...
    if len(command) == 1:
        return False, f'empty protocol', None
    # protocol = command_raw.replace('protocol', '')  # ' home;goto 1'
    # lines = protocol.split('\n')  # ' home', 'goto 1'
    # # print(f'check_protocol()...lines={lines}')
    # # clear protocol command list
    # global _protocol_command_list
    # global _protocol_command_list_index
    # _protocol_command_list = []
    # _protocol_command_list_index = -1
    # # generate protocol command and generate command string list
    # # for command in lines:
    # for i in range(0, len(lines)):
    #     line = lines[i]
    #     line = line.strip()
    #     command = line.split()
    #     cmd = command[0]
    #     if cmd == 'home':
    #         _protocol_command_list.append('magnet home')
    #         _protocol_command_list.append('syringe go_until')
    #         _protocol_command_list.append('syringe release_switch')
    #         _protocol_command_list.append('syringe home_shift')
    #         _protocol_command_list.append('chamber home')
    #     elif cmd == 'magnet':
    #         _protocol_command_list.append(line)
    #     elif cmd == 'goto':
    #         _protocol_command_list.append('chamber ' + line)
    #     elif cmd == 'pumping':
    #         _protocol_command_list.append('syringe ' + line)
    #     elif cmd == 'waiting':
    #         _protocol_command_list.append(line)
    #     else:
    #         _protocol_command_list = []
    #         _protocol_command_list_index = -1
    #         return False, f'invlaid protocol command {cmd}', None
    # print(_protocol_command_list)
    return True, None, None


def start_protocol_check(command):
    # # clear index
    # global _protocol_command_list_index
    # _protocol_command_list_index = 0
    # # get command
    # if len(_protocol_command_list) == 0:
    #     return True, None, None
    # command = _protocol_command_list[_protocol_command_list_index]
    # # start command
    # start_command(command)
    return True, None, None


def wait_protocol_check(command):
    # global _protocol_command_list_index
    # # get command
    # if len(_protocol_command_list) == 0:
    #     return False  # not waiting
    # command = _protocol_command_list[_protocol_command_list_index]
    # # call wait function
    # waiting = wait_command(command)
    # # check waiting
    # if waiting:
    #     return True  # waiting
    # # not waiting, go to next command
    # _protocol_command_list_index += 1
    # # check if all done
    # if _protocol_command_list_index >= len(_protocol_command_list):
    #     _protocol_command_list_index = -1
    #     return False  # not waiting
    # # call next start function
    # command = _protocol_command_list[_protocol_command_list_index]
    # start_command(command)
    return False  # not waiting


def stop_protocol_check(command):
    # global _protocol_command_list_index
    # # get command
    # if len(_protocol_command_list) == 0:
    #     return
    # command = _protocol_command_list[_protocol_command_list_index]
    # # call stop fucntion
    # stop_command(command)
    # # clear index
    # _protocol_command_list_index = -1
    return True, None, None
