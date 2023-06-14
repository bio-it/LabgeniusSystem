# -*- coding: utf-8 -*-
###############################################################################
# command_magnet_status.py
###############################################################################
import magneto.actuators.l6470 as l6470
from magneto.actuators.hardware_config import magnet


#######################################
# get magnet status
#######################################
def check(command):
    return True, None, None

def start(command):
    running = magnet.is_busy()
    data = {'running': running}
    return (True, None, data)

def wait(command):
    return False

def stop(command):
    return (True, None, None)

# command_magnet_status.py
