# -*- coding: utf-8 -*-
###############################################################################
# command_print.py
###############################################################################

g_message = ''


def check(command):
    return True, None, None


def start(command):
    global g_message
    command = command.split()
    if len(command) < 2:
        g_message = ''
    else:
        g_message = ' '.join(command[1:])
    return True, None, None


def wait(command):
    return False  # not waiting


def stop(command):
    global g_message
    g_message = ''
    return True, None, None


def dir(command):
    return f''


def get_message():
    return g_message

# command_print.py
