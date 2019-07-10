# pcrEmulator.py
# -*- coding: utf-8 -*-

import threading
import time

import zmq

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Main loop
context = zmq.Context()
listener = context.socket(zmq.REP)
listener.bind('tcp://*:6060')
listener.setsockopt(zmq.RCVTIMEO, 500)


# For emulator data

# state

class Emulator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False

        # False : idle, True: running
        self.emulatorState = False
        self.emulatorTemp = 25.0
        self.emulatorTargetTemp = 25.0

    def run(self):
    	while True:
    		# Check current state is running.
    		if self.emulatorState:
	    		if '%.1f' % self.emulatorTemp > '%.1f' % self.emulatorTargetTemp:
    				self.emulatorTemp -= 0.1
    			elif '%.1f' % self.emulatorTemp < '%.1f' % self.emulatorTargetTemp:
	    			self.emulatorTemp += 0.1
    		time.sleep(0.1)

    def setTemperature(self, targetTemp):
    	self.emulatorTargetTemp = targetTemp
    	self.emulatorState = True

    def getTemperature(self):
    	return self.emulatorTemp

    def stopEmulator(self):
    	self.emulatorState = False
    	self.emulatorTemp = 25.0
    	self.emulatorTargetTemp = 25.0

    def getState(self):
    	return self.emulatorState


# Start emulator
emulator = Emulator()
emulator.start()

while True:
	try:
		message = listener.recv_json()
	except:
		# Ignore the
		logger.info("ignore")
		continue

	if message['command'] == 'T':
		# target temp
		targetTemp = message["targetTemp"]

		logging.info("Command T received : %f" % targetTemp)
		emulator.setTemperature(targetTemp)
	elif message['command'] == 'C':
		currentTemp = emulator.getTemperature()
		currentState = emulator.getState()

		logging.info("Command C received : %s, %f" % (currentState, currentTemp))
		listener.send_json({'result':'ok', 'state':'%s'%currentState, 'temp':'%.1f' % currentTemp})
	elif message['command'] == 'S':
		currentState = emulator.getState()
		logging.info("Command S received : %d" % currentState)

		if currentState:
			emulator.stopEmulator()
			listener.send_json({'result':'ok'})
		else:
			listener.send_json({'result':'fail'})

