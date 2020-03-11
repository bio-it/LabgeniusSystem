# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import request
import logging
import requests

import json

from api import util

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoryList(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok',
			'histories' : util.getHistoryList()
		}

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok',
			'histories' : util.getHistoryList()
		}

		return response, 200

class HistoryGraphData(Resource):
	def post(self):
		# Check the current state first
		requestData = request.data
		requestData = requestData.decode('utf-8')

		try:
			idx = int(requestData)
			data = util.getHistoryGraphData(idx)

			if data == "":
				response = {
					'result' : 'fail',
					'reason' : "Invalid idx or data is not exist."
				}
			else:
				response = {
					'result' : 'ok',
					'graphData' : data
				}
		except Exception as e:
			logger.info(str(e))
			response = {
				'result' : 'fail',
				'reason' : 'Invalid protocol idx parameter.'
			}

		return response, 200

class HistoryTempData(Resource):
	def post(self):
		# Check the current state first
		requestData = request.data
		requestData = requestData.decode('utf-8')

		try:
			idx = int(requestData)
			data = util.getHistoryTempData(idx)

			if data == "":
				response = {
					'result' : 'fail',
					'reason' : "Invalid idx or data is not exist."
				}
			else:
				response = {
					'result' : 'ok',
					'tempData' : data
				}
		except Exception as e:
			logger.info(str(e))
			response = {
				'result' : 'fail',
				'reason' : 'Invalid protocol idx parameter.'
			}

		return response, 200