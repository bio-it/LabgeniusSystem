# -*- coding: utf-8 -*-
###############################################################################
# command_syringe_status.py
###############################################################################
import magneto.actuators.l6470 as l6470
from magneto.actuators.hardware_config import syringe


#######################################
# get syringe status
#######################################
def check(command):
    return True, None, None

def start(command):
    running = syringe.is_busy()
    driver_position = syringe.get_pos()
    encoder_position = syringe.get_encoder_position()
    registers = syringe.get_registers()
    data = {'running': running, 'driver_position': driver_position, 'encoder_position': encoder_position, 'registers': registers}
    return (True, None, data)

def wait(command):
    return False

def stop(command):
    return (True, None, None)


# def _make_stepper_status_dict(position, velocity, status):
#     status_dict = {'pos': 1.0, 'speed': 1.0, 'swon': False, 'busy': True, 'uvlo': True,'ocd': False, 
#      'thwrn': False, 'thsd': False, 'notperfcmd': False, 'wrongcmd': False, 'stalldet': False }
#     status_dict['pos'] = round(position, 2)
#     status_dict['speed'] = round(velocity, 2)
#     status_dict['swon'] = (status & l6470.STATUS_BIT_SW_F) == l6470.STATUS_BIT_SW_F
#     status_dict['busy'] = (status & l6470.STATUS_BIT_BUSY) != l6470.STATUS_BIT_BUSY
#     status_dict['uvlo'] = (status & l6470.STATUS_BIT_UVLO) != l6470.STATUS_BIT_UVLO 
#     status_dict['ocd'] = (status & l6470.STATUS_BIT_OCD) != l6470.STATUS_BIT_OCD    
#     status_dict['thwrn'] = (status & l6470.STATUS_BIT_TH_WRN) != l6470.STATUS_BIT_TH_WRN
#     status_dict['thsd'] = (status & l6470.STATUS_BIT_TH_SD) != l6470.STATUS_BIT_TH_SD 
#     status_dict['notperfcmd'] = (status & l6470.STATUS_BIT_NOTPERF_CMD) == l6470.STATUS_BIT_NOTPERF_CMD
#     status_dict['wrongcmd'] = (status & l6470.STATUS_BIT_WRONG_CMD) == l6470.STATUS_BIT_WRONG_CMD
#     status_dict['stalldet'] = (status & l6470.STATUS_BIT_STEP_LOSSES) != l6470.STATUS_BIT_STEP_LOSSES
#     return status_dict



# command_syringe_status.py
