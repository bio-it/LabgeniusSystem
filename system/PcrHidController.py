# pcrEmulator.py
# -*- coding: utf-8 -*-

import time
import os

import zmq
import hid
import struct

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PCR_PORT = os.environ.get('PCR_PORT', '7001')

# Main loop
context = zmq.Context()
listener = context.socket(zmq.REP)
listener.bind('tcp://*:%s' % PCR_PORT)

# listener.setsockopt(zmq.RCVTIMEO, 500)

vid = 0x04d8
pid = 0x0041

dev = hid.Device(vid, pid)

serialNumber = dev.serial

while True:
	try:
		message = listener.recv_json()
	except Exception as e:
		# Ignore the
		logger.info(e)
		logger.info("ignore")
		continue

	# setup data
	print(message)
	send_buffer = [message["cmd"], int(message["currentTargetTemp"])]

	# pid data
	send_buffer += [0] * 16

	# led control data
	send_buffer += [message["ledControl"], message["led_wg"], message["led_r"], message["led_g"], message["led_b"], message["compensation"]]

	# dummy
	send_buffer += [0] * 40

	dev.write(bytes(send_buffer))
	received_buffer = dev.read(64)

	# device information
	state = int(received_buffer[0])
	temperature = struct.unpack('<f', received_buffer[3:7])[0]
	photodiode = int(received_buffer[7]) << 8 | int(received_buffer[8])
	currentError = int(received_buffer[9])

	print(state, temperature, photodiode, currentError)

	listener.send_json({"temp":'%.1f' % temperature, "state":state, "photodiode":photodiode, "currentError":currentError, "serialNumber":serialNumber})

# No function about the Fan.

