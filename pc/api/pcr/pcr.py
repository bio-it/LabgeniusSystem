# -*- coding: utf-8 -*-

from flask_restful import Resource

# Member functions for pcr task
from api.pcr import task

pcrThread = task.PCRThread()
pcrThread.start()

# No any parameter

class Start(Resource):
	def get(self):
		# Check the current state first
		print("test1")

		response = {
			'result' : 'ok'
		}

		return response, 200
