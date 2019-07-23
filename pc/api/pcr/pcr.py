# -*- coding: utf-8 -*-

from flask_restful import Resource

# Member functions for pcr task
from api.pcr import task

import logging

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

pcrThread = task.PCRThread()
pcrThread.start()

# No any parameter

class Start(Resource):
	def get(self):
		# Check the current state first
		logger.info("test1")

		if pcrThread.isRunning():
			response = {
				'result' : 'fail',
				'reason' : 'already started'
			}
		else:
			pcrThread.startPCR()
			response = {
				'result' : 'ok'
			}

		return response, 200

class Stop(Resource):
	def get(self):
		# Check the current state first
		logger.info("test2")

		if pcrThread.isRunning():
			pcrThread.stopPCR()
			response = {
				'result' : 'ok'
			}
		else:
			response = {
				'result' : 'fail',
				'reason' : 'PCR is not running now.'
			}

		return response, 200

class Status(Resource):
	def get(self):
		# Check the current state first
		logger.info("test3")

		logger.info(pcrThread.getStatus())

		response = {
			'result' : 'ok',
			'data' : 'test'
		}

		return response, 200
