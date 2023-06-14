# -*- coding: utf-8 -*-

from api import task_worker
from flask_restful import Resource

# Member functions for pcr task
from api.task_worker import TaskWorker

import logging

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#pcrThread = task.PCRThread()
#pcrThread.start()

# No any parameter

class Start(Resource):
	def get(self):
		# Check the current state first
		task_worker = TaskWorker.instance()

		if task_worker.isRunning():
			response = {
				'result' : 'fail',
				'reason' : 'already started'
			}
		else:
			task_worker._start()
			response = {
				'result' : 'ok'
			}
		

		return response, 200

	def post(self):
		# Check the current state first
		task_worker = TaskWorker.instance()

		if task_worker.isRunning():
			response = {
				'result' : 'fail',
				'reason' : 'already started'
			}
		else:
			task_worker._start()
			response = {
				'result' : 'ok'
			}

		return response, 200

class Stop(Resource):
	def get(self):
		# Check the current state first
		task_worker = TaskWorker.instance()

		if task_worker.isRunning():
			task_worker.stopPCR()
			response = {
				'result' : 'ok'
			}
		else:
			response = {
				'result' : 'fail',
				'reason' : 'PCR is not running now.'
			}


		return response, 200

	def post(self):
		# Check the current state first
		task_worker = TaskWorker.instance()
		
		if task_worker.isRunning():
			task_worker.stopPCR()
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
		response = {
			'result' : 'ok',
			'data' : TaskWorker.instance().getStatus()
		}
		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok',
			'data' : TaskWorker.instance().getStatus()
		}

		return response, 200
