# -*- coding: utf-8 -*-
###############################################################################
# magneto_task.py
###############################################################################
import threading
import time
from magneto.command_handler.command_handler import check_command, is_instant, start_command, wait_command, stop_command
from magneto.command_handler.command_handler import is_stop_command, stop, is_get_status_command
from magneto.command_handler.command_handler import dir_command
from magneto.actuators.hardware_config import chamber, syringe, filter, magnet
# import magneto.actuators.l6470 as l6470

# thread lock
g_thread_lock = threading.Lock()

# magneto task thread


class MagnetoTask(threading.Thread):
    def __init__(self):
        # init thread
        threading.Thread.__init__(self)
        self.daemon = True  # Daemon is important
        self.running = False
        self.current_command = ''

    def run(self):
        # task thread loop
        while True:
            with g_thread_lock:
                if self.running:
                    # check if command finished
                    if self.current_command != '':
                        self.running = wait_command(self.current_command)
                        if not self.running:
                            self.current_command = ''
                syringe.update_encoder_multi_turn()
                chamber.update_encoder_multi_turn()
                # time.sleep(0.05)  # 50 millesecond but almost take 100ms
                # time.sleep(0.02)  # 50 millesecond but almost take 40ms ?
                # time.sleep(0.01)  # 50 millesecond but almost take 20ms ?

    def run_command(self, command):
        # command: single string
        # returns (result, reason, data)
        with g_thread_lock:
            # process stop command
            if is_stop_command(command):
                return self._stop_command()
            # process get status commmand
            if is_get_status_command(command):
                return self._get_status()
            # check command
            (result, reason, data) = check_command(command)
            if result == False:
                return (result, reason, data)
            # process instant and not-instant commands
            if is_instant(command):
                return start_command(command)
            else:
                if self.running:
                    return (False, f'can not run this command during running!', None)
                self.current_command = command
                self.running = True
                return start_command(command)

    def is_running(self):
        with g_thread_lock:
            return self.running

    def _stop_command(self):
        '''
        stop command is processsed here because the current command is maintained here.
        '''
        # chamber.soft_stop()
        # syringe.soft_stop()
        # filter.soft_stop()
        # chamber.clear_status()
        # syringe.clear_status()
        # filter.clear_status()
        # magnet.stop()
        stop()
        if self.running:
            if self.current_command != '':
                self.running = False
                stop_command(self.current_command)
                self.current_command = ''
        return (True, None, None)

    def _get_status(self):
        '''
        get status is processed here because this command is not to be save in the current command
        '''
        running_command = dir_command(self.current_command)
        data = {'running': self.running, 'runningCommand': running_command}

        return (True, None, data)

# class MagnetoTask(threading.Thread):

# magneto_task.py
