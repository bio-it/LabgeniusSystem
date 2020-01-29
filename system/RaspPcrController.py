# pcrEmulator.py
# -*- coding: utf-8 -*-

import time
import os

import zmq
import smbus

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PCR_PORT = os.environ.get('PCR_PORT', '7001')

# Main loop
context = zmq.Context()
listener = context.socket(zmq.REP)
listener.bind('tcp://*:%s' % PCR_PORT)

# listener.setsockopt(zmq.RCVTIMEO, 500)
# For emulator data

# state

"""
class Emulator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

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
    		time.sleep(0.05)

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
"""

i2c = smbus.SMBus(1)
ADDRESS = 0x08

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

		send_data = [ord('T'), int(targetTemp), 0x00]
		i2c.write_i2c_block_data(ADDRESS, 0x00, send_data)

		listener.send_json({'result':'ok'})
	elif message['command'] == 'C':
		send_data = [ord('C'), 0x00, 0x00]
		i2c.write_i2c_block_data(ADDRESS, 0x00, send_data)

		received_data = i2c.read_i2c_block_data(ADDRESS, 0x00)

		logger.info("test : %d %d %d " % (received_data[0], received_data[1], received_data[2]))

		currentTemp = float(received_data[1])
		currentState = 0

		logging.info("Command C received : %s, %f" % (currentState, currentTemp))
		listener.send_json({'result':'ok', 'state':'%s'%currentState, 'temp':'%.1f' % currentTemp})
	elif message['command'] == 'S':
		send_data = [ord('S'), 0x00, 0x00]
		i2c.write_i2c_block_data(ADDRESS, 0x00, send_data)

		listener.send_json({'result':'ok'})
	elif message['command'] == 'R': # reset
		send_data = [ord('R'), 0x00, 0x00]
		i2c.write_i2c_block_data(ADDRESS, 0x00, send_data)

		listener.send_json({'result':'ok'})

# No function about the Fan.

