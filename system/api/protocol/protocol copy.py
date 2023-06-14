# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import request
from api.task_worker import TaskWorker
import logging
import requests

import json

from api import util

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

errorMessages = ['Invalid protocol name or protocol index(code:0)', 'Invalid filter data, not enough filter(code:1)', '']



def checkProtocol(protocol:dict):
	'''
	Check protocol is valid
		protocol params error code 	: 0x
		filter params error code 	: 1x
		PCR Prococol error code 	: 2x
		Magneto protocol error code : 3x
	'''
	# Check params in protocol
	params = { 'filters' : dict, 'PCR' : list, magneto : list }
	for param, _type in params.items():
		if param not in protocol:
			response = {
				'result' : False,
				'reason' : 'Invalid protocol data, no %s in protocol(code:00)' % param
			}
			return response
		elif type(protocol[param]) != _type:
			response = {
				'result' : False,
				'reason' : 'Invalid protocol data, %s type error(code:01)' % param
			}
			return response
		elif len(protocol[param]) == 0:
			response = {
				'result' : False,
				'reason' : 'Invalid protocol data, %s is empty(code:02)' % param
			}
			return response


	# Check the validation. 
	allFilters = ['FAM', 'HEX', 'ROX', 'CY5']
	filterKeys = ['name', 'value', 'use']

	# check filters data is valid
	for index, value in enumerate(allFilters):
		if not protocol['filters'].get(value):
			response = {
				'result' : False,
				'reason' : 'Invalid filters data(code:10)'
			}
			return response
		for key in filterKeys:
			if not protocol['filters'][value].get(key):
				response = {
					'result' : False,
					'reason' : 'Invalid filter format, filter consists of name, value and use(code:11)'
				}
			return response
	

	currentLabel = 0
	lastGotoLine = -1
	lineNumber = 0
	shotCount = 0
	response = { 'result' : True }

	# Check actions is valid
	for action in protocol['PCR']:
		label = action.get('label')
		temp  = action.get('temp')
		time  = action.get('time')

		lineNumber += 1
		if type(label) != str: # Check label is str 
			response = {
				'result' : False,
				'reason' : 'Invalid type for label, line %d(code:20)' % lineNumber
			}
			break

		if label == 'SHOT': # Label is SHOT
			shotCount += 1
			if temp or time:
				response = {
					'result' : False,
					'reason' : 'SHOT action must be temp and time params are empty, line : %d(code:21)' % lineNumber
				}
				break
		else: # Label is 'GOTO' or integer
			if type(temp) != int or type(time) != int: #  Check type paramters (temp, time)
				response = {
					'result' : False,
					'reason' : 'Invalid type for temp or time, line %d(code:22)' % lineNumber
				}
				break

			
			if label == 'GOTO': # Check GOTO label
				# Correct condition of GOTO target label
				if currentLabel != 0 and currentLabel >= temp and lastGotoLine <= (temp+shotCount):
					# Check count of GOTO count
					if not 1 <= time <= 100:
						response = {
							'result' : False,
							'reason' : 'Invalid GOTO count(1~100), line %d(code:23)' % lineNumber
						}
						break
					# Save the last GOTO line number
					lastGotoLine = lineNumber
			
			else: # Label is integer
				if not label.isdegit(): # Check label is consist of numbers
					response = {
						'result' : False,
						'reason' : 'Invalud label value, line %d(code:24)' % lineNumber
					}
					break

				if currentLabel + 1 != int(label):
					response = {
						'result' : False,
						'reason' : 'Invalid label numbering, line %d(code:25)'
					}
					break

				if not 4 <= temp <= 104:
					response = {
						'result' : False,
						'reason' : 'Invalid temperature range(4~104), line %d(code:26)'
					}
					break

				if not 1 <= time <= 999:
					response = {
						'result' : False,
						'reason' : 'Invalid time range(1~999), line %d(code:27)' % lineNumber
					}
					break
				currentLabel = int(label)

		# check error in PCR Protocol
		# if not response['result']:
		# 	return response
		# end of line number check
		
		# TODO : check magneto protocol
		# check the validation of Magneto protocol.
		# lineNumber = 0
		# magneto = protocol['magneto']
		
		# magnetoResult = ""
		# commandList = [ 'goto', 'filter', 'mixing', 'waiting', 
		# 				'pumping up', 'pumping sup', 'pumping down', 'pumping sdown', 
		# 				'ready', 'home', 'magnet on', 'magnet off', 'heating', 'pcr']
		# for line in magneto:
		# 	lineNumber += 1
		# 	if type(line) != str:
		# 		response = {
		# 			'result' : False,
		# 			'reason' : 'Invalid type in magneto protocol, line %d (code:30)' % lineNumber
		# 		}
		# 	line = line.strip()
		# 	# skip empty line 
		# 	if len(line) == 0:
		# 		continue
		# 	# skip % line 
		# 	elif line[0] == '%':
		# 		continue

		# 	command = line.split(' ')
	
	return response

def convertToProtocol(protocolLines):
	# index of #
	index = protocolLines.index('#')

	result = []
	for line in protocolLines[0:index]:
		if line == 'SHOT':
			result.append({"label":"SHOT", "temp":0.0, "time":0})
		else:
			data = line.split("\t")
			result.append({"label":"%s" % data[0], "temp":"%.1f" % float(data[1]), "time":"%d" % int(data[2])})

	# magneto protocol
	magnetoProtocol = protocolLines[index+1:]
	return json.dumps(result), json.dumps(magnetoProtocol)

# def convertToProtocol(protocolLines):


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
			print(idx)
			protocol = util.getProtocol(idx)

			if len(protocol) == 0:
				response = {
					'result' : False,
					'reason' : 'Failed to load the protocol(database error).'
				}
			else:
				# Don't use request message
				# Request the PCR status
				# status = requests.post(('http://%s:6009/api/pcr/status' % util.getIpAddress()))

				# if not status.json()["data"]["running"]: not use

				# not running
				if not TaskWorker.instance().isRunning():
					# Setting the protocol first
					# name, filters, filterNames, filterCts, protocol, magnetoProtocol
					util.setRecentProtocol(protocol["name"], protocol["filters"], protocol["filterNames"], protocol["filterCts"], protocol["protocol"], protocol["magnetoProtocol"])
					
					# Don't use request messages
					# result = requests.post(('http://%s:6009/api/pcr/reloadProtocol' % util.getIpAddress()))

					# logger.info(result.json())

					# if result.json()["result"] == "ok":
					# 	response = {
					# 		'result' : 'ok'
					# 	}
					# else:
					# 	response = {
					# 		'result' : False,
					# 		'reason' : 'Can\'t change the protocol when the PCR is running'
					# 	}

					if TaskWorker.instance().reloadProtocol():
						response = {
							'result' : 'ok'
						}
					else:
						response = {
							'result' : False,
							'reason' : 'Can\'t change the protocol when the PCR is running'
						}
				else:
					# running the PCR
					response = {
						'result' : False,
						'reason' : 'Can\'t change the protocol when the PCR is running'
					}

		except Exception as e:
			logger.info(str(e))
			response = {
				'result' : False,
				'reason' : 'Invalid protocol idx parameter.'
			}

		return response, 200

class CreateProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')
		protocol = requestData.split('\r\n')

		if len(protocol) < 2:
			response = {
				'result' : False,
				'reason' : 'No protocol data or name data.'
			}
		else:
			response = checkProtocol(protocol[1:])

			if response['result'] == 'ok':
				# save the protocol into the database with name
				name = protocol[0]

				if util.checkProtocolExist(name):
					response = {
						'result' : False,
						'reason' : 'Already exist the protocol name.'
					}
				else:
					# need to make the protocol type of string
					filters = protocol[1]
					filterNames = protocol[2]
					filterCts = protocol[3]

					protocol, magnetoProtocol = convertToProtocol(protocol[4:])
					logger.info(protocol)
					logger.info(magnetoProtocol)
					util.insertProtocol(name, filters, protocol, magnetoProtocol)
					# util.insertProtocol(name, filters, filterNames, filterCts, protocol, magnetoProtocol)

		return response, 200

class DeleteProtocol(Resource):
	def post(self):
		requestData = request.data
		requestData = requestData.decode('utf-8')

		try:
			idx = int(requestData)

			# check protocol name
			currentProtocol = util.getProtocol(idx)

			if len(currentProtocol) == 0:
				response = {
					'result' : False,
					'reason' : 'Invalid protocol data for idx'
				}
			else:
				currentProtocolName = currentProtocol["name"]

				# Check the current protocol is same protocol.
				# status = requests.post(('http://%s:6009/api/task/status' % util.getIpAddress()))
				status = TaskWorker.instance().getStatus()

				# if status.json()["data"]["protocolName"] == currentProtocolName:
				if status["protocolName"] == currentProtocolName:
					# check the device is running.
					# if status.json()["data"]["running"]:
					if status["running"]:
						response = {
							'result' : False,
							'reason' : 'this protocol is running now.'
						}
					else:
						result = util.deleteProtocol(idx)

						if result:
							# remove the recent protocol
							util.clearRecentProtocol()

							# Don't use request messages
							# result = requests.post(('http://%s:6009/api/pcr/reloadProtocol' % util.getIpAddress()))
							# logger.info(result.json())

							# if result.json()["result"] == "ok":
							# 	response = {
							# 		'result' : 'ok'
							# 	}
							# else:
							# 	response = {
							# 		'result' : False,
							# 		'reason' : 'Can\'t change the protocol when the PCR is running'
							# 	}

							if TaskWorker.instance().reloadProtocol():
								response = {
									'result' : 'ok'
								}
							else:
								response = {
									'result' : False,
									'reason' : 'Can\'t change the protocol when the PCR is running'
								}
							
						else:
							response = {
								'result' : False,
								'reason' : 'Invalid range of idx parameter'
							}
				else:
					result = util.deleteProtocol(idx)

					if result:
						# remove the recent protocol
						util.clearRecentProtocol()

						# Don't use request messages
						# result = requests.post(('http://%s:6009/api/pcr/reloadProtocol' % util.getIpAddress()))
						# logger.info(result.json())

						# if result.json()["result"] == "ok":
						# 	response = {
						# 		'result' : 'ok'
						# 	}
						# else:
						# 	response = {
						# 		'result' : False,
						# 		'reason' : 'Can\'t change the protocol when the PCR is running'
						# 	}

						if TaskWorker.instance().reloadProtocol():
							response = {
								'result' : 'ok'
							}
						else:
							response = {
								'result' : False,
								'reason' : 'Can\'t change the protocol when the PCR is running'
							}
					else:
						response = {
							'result' : False,
							'reason' : 'Invalid range of idx parameter'
						}
		except Exception as e:
			import traceback
			print(traceback.format_exc())
			logger.info(str(e))
			response = {
				'result' : False,
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
				'result' : False,
				'reason' : 'Invalid protocol data.'
			}
		else:
			try:
				idx = int(lines[0])

				response = checkProtocol(lines[1:])
				
				if response['result'] == 'ok':
					# check protocol name
					currentProtocol = util.getProtocol(idx)

					if len(currentProtocol) == 0:
						response = {
							'result' : False,
							'reason' : 'Invalid protocol data for idx'
						}
					else:
						currentProtocolName = currentProtocol["name"]
						# Check the current protocol is same protocol.
						# status = requests.post(('http://%s:6009/api/task/status' % util.getIpAddress()))
						status = TaskWorker.instance().getStatus()
						# getting the protocol data from user
						filters = lines[1]
						filterNames = lines[2]
						filterCts = lines[3]
						protocol, magnetoProtocol = convertToProtocol(lines[4:])

						# if status.json()["data"]["protocolName"] == currentProtocolName:
						if status["protocolName"] == currentProtocolName:
							# check the device is running.
							# if status.json()["data"]["running"]:
							if status["running"]:
								response = {
									'result' : False,
									'reason' : 'this protocol is running now.'
								}
							else:
								# not running, change the protocol first.
								result = util.editProtocol(idx, filters, filterNames, filterCts, protocol, magnetoProtocol)
								logger.info(result)

								if result:
									# need to reload the protocols
									util.setRecentProtocol(currentProtocolName, filters, filterNames, filterCts, protocol, magnetoProtocol)
									
									# Don't use request messages
									# result = requests.post(('http://%s:6009/api/pcr/reloadProtocol' % util.getIpAddress()))

									# logger.info(result.json())
									
									# if result.json()["result"] == "ok":
									# 	response = {
									# 		'result' : 'ok'
									# 	}
									# else:
									# 	response = {
									# 		'result' : False,
									# 		'reason' : 'Can\'t change the protocol when the PCR is running'
									# 	}

									if TaskWorker.instance().reloadProtocol():
										response = {
											'result' : 'ok'
										}
									else:
										response = {
											'result' : False,
											'reason' : 'Can\'t change the protocol when the PCR is running'
										}
								else:
									response = {
										'result' : False,
										'reason' : 'Invalid range of idx parameter'
									}
						else:
							# change the protocol.
							result = util.editProtocol(idx, filters, filterNames, filterCts, protocol, magnetoProtocol)
							logger.info(result)

							if result:
								response = {
									'result' : 'ok',
								}
							else:
								response = {
									'result' : False,
									'reason' : 'Invalid range of idx parameter'
								}
			except Exception as e:
				import traceback
				print(traceback.format_exc())
				logger.info(str(e))
				response = {
					'result' : False,
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


class ReloadProtocol(Resource):
	def get(self):
		result = TaskWorker.instance().reloadProtocol()

		if result:
			response = {
				'result' : 'ok'
			}
		else:
			response = {
				'result' : False,
				'reason' : 'PCR is running.'
			}

		return response, 200

	def post(self):
		result = TaskWorker.instance().reloadProtocol()

		if result:
			response = {
				'result' : 'ok'
			}
		else:
			response = {
				'result' : False,
				'reason' : 'PCR is running.'
			}

		return response, 200