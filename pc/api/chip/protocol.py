# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import request
import logging
import requests

import json

from api.chip import util

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def checkProtocol(protocol):
	# Check the validation.
	if len(protocol) <= 3:
		response = {
			'result' : 'fail',
			'reason' : 'Invalid protocol data, not enough line(code:1)'
		}
	else:
		# Command list
		commandList = ['goto', 'filter', 'mixing', 'waiting', 'pumping up', 'pumping sup', 'pumping down', 'pumping sdown', 'ready', 'home', 'magnet on', 'magnet off', 'heating', 'pcr']

	response = {
		'result' : 'fail',
		'reason' : 'Not yet implemented'
	}

	return response

def convertToProtocol(protocolLines):
	result = []
	for line in protocolLines:
		if line == 'SHOT':
			result.append({"label":"SHOT", "temp":0.0, "time":0})
		else:
			data = line.split("\t")
			result.append({"label":"%s" % data[0], "temp":"%.1f" % float(data[1]), "time":"%d" % int(data[2])})
	return json.dumps(result)

class ProtocolList(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok',
			'protocols' : util.getProtocolList()
		}

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok',
			'protocols' : util.getProtocolList()
		}

		return response, 200

# Need to get the parameter
class ProtocolSelect(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')

		try:
			idx = int(requestData)
			protocol = util.getProtocol(idx)

			if len(protocol) == 0:
				response = {
					'result' : 'fail',
					'reason' : 'Failed to load the protocol(database error).'
				}
			else:
				# Request the PCR status
				status = requests.post('http://210.115.227.99:6009/api/pcr/status')

				# not running
				if not status.json()["data"]["running"]:
					# Setting the protocol first
					util.setRecentProtocol(protocol[0][1], protocol[0][2], protocol[0][4])

					result = requests.post('http://210.115.227.99:6009/api/pcr/reloadProtocol')

					logger.info(result.json())

					if result.json()["result"] == "ok":
						response = {
							'result' : 'ok'
						}
					else:
						response = {
							'result' : 'fail',
							'reason' : 'Can\'t change the protocol when the PCR is running'
						}
				else:
					# running the PCR
					response = {
						'result' : 'fail',
						'reason' : 'Can\'t change the protocol when the PCR is running'
					}

		except Exception as e:
			logger.info(str(e))
			response = {
				'result' : 'fail',
				'reason' : 'Invalid protocol idx parameter.'
			}

		return response, 200

class NewProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')
		protocol = requestData.split('\r\n')

		if len(protocol) < 2:
			response = {
				'result' : 'fail',
				'reason' : 'No protocol data or name data.'
			}
		else:
			response = checkProtocol(protocol[1:])

			if response['result'] == 'ok':
				# save the protocol into the database with name
				# TODO: name validation
				name = protocol[0]

				# need to make the protocol type of string
				filters = protocol[1]
				protocol = convertToProtocol(protocol[2:])

				util.insertNewProtocol(name, filters, protocol)

		return response, 200

class DeleteProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')

		try:
			idx = int(requestData)
			result = util.deleteProtocol(idx)

			if result:
				response = {
					'result' : 'ok',
				}
			else:
				response = {
					'result' : 'fail',
					'reason' : 'Invalid range of idx parameter'
				}
		except:
			response = {
				'result' : 'fail',
				'reason' : 'Invalid protocol idx parameter.'
			}

		return response, 200

class EditProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')
		lines = requestData.split('\r\n')

		# Check lines
		if len(lines) < 4:
			response = {
				'result' : 'fail',
				'reason' : 'Invalid protocol data.'
			}
		else:
			try:
				idx = int(lines[0])

				response = checkProtocol(lines[1:])

				if response['result'] == 'ok':
					# save the protocol into the database with name

					# need to make the protocol type of string
					filters = lines[1]
					protocol = convertToProtocol(lines[2:])

					result = util.editProtocol(idx, filters, protocol)
					logger.info(result)

					if result:
						response = {
							'result' : 'ok',
						}
					else:
						response = {
							'result' : 'fail',
							'reason' : 'Invalid range of idx parameter'
						}
			except:
				response = {
					'result' : 'fail',
					'reason' : 'Invalid protocol idx parameter.'
				}

		return response, 200

class CheckProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')
		protocol = requestData.split('\r\n')

		response = checkProtocol(protocol)

		return response, 200