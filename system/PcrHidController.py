# -*- coding: utf-8 -*-

from cmath import exp
import json
import time
import os
from math import fabs

import zmq
import hid
import smbus 

import logging
import threading 
from datetime import datetime, timedelta
from enum import IntEnum
from UserDefs import *

from magneto.actuators.l6470_sc18is602b_interface import L6470Sc18is602bInterface
from magneto.actuators.filter import Filter

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PCR_PORT = os.environ.get('PCR_PORT', '7001')
TIMER_DURATION = 50
DEFAULT_PIDS = [
	{'start_temp' : 25.0, 'target_temp' : 95.0, 'Kp' : 460.0, 'Kd' : 3000.0, 'Ki' : 0.2},
	{'start_temp' : 95.0, 'target_temp' : 60.0, 'Kp' : 250.0, 'Kd' : 1000.0, 'Ki' : 0.3},
	{'start_temp' : 60.0, 'target_temp' : 72.0, 'Kp' : 350.0, 'Kd' : 3000.0, 'Ki' : 0.11},
	{'start_temp' : 72.0, 'target_temp' : 95.0, 'Kp' : 460.0, 'Kd' : 3000.0, 'Ki' : 0.2},
	{'start_temp' : 96.0, 'target_temp' : 50.0, 'Kp' : 500.0, 'Kd' : 1000.0, 'Ki' : 0.3}
]

class Controller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

		# HID Device params
		vendor_id = 0x04d8
		product_id = 0x0041
		self.device = hid.Device(vendor_id, product_id)

		self.serial_number = self.device.serial
		self.currentError = 0

		self.txBuffer = TxBuffer()
		self.rxBuffer = RxBuffer()


		self.pids = DEFAULT_PIDS
		self.pid = self.pids[0]

		self.running = False
		self.currentCommand = Command.READY
		self.completePCR = False
		self.targetArrival = False
		self.targetArrivalFlag = False
		self.targetArrivalDelta = 0.5
		self.freeRunning = False
		self.freeRunningCounter = 0

		# Timed Loop params
		self.leftSec = 0				# current action remain time
		self.leftTotalSec = 0			# total remain time
		self.currentActionNumber = -1	# current action number
		self.totalActionNumber = 0		# total action number
		self.leftGotoCount = -1			# remain goto count
		self.startTime = None			# pcr start time
		self.elapsedTime = ''			# 
		

		self.state = State.READY
		self.stateString = 'idle'

		self.currentTemp = 20.0			# current pcr chip temperature
		self.prevTargetTemp = 25.0		# previous target temperature
		self.currentTargetTemp = 25.0	# current target temperature

		# need to setup
		self.compensation = 30			# 
		self.currentError = 0			# error code
		self.integralMax = 2600.		# integral max value (2600.0 or 5200.0)
		self.FLRelativeMax = 3600.		# 

		# Detection params 
		self.leds = { 'FAM' : 1, 'HEX' : 1, 'ROX' : 1, 'CY5' : 1 } # turn off : 1, turn on : 0
		self.led_control = 1					# led control param
		self.leds_pwm = [0] * 4					# leds pwm param
		# self.leds_pwm = [255] * 4
		self.currentPhotodiode = 0				# current photodiode value	
		self.photodiodes = [[], [], [], []]		# photodiodes values to List

		# for filter 
		logger.info('Initialize Filter')
		self.i2c = smbus.SMBus(1)
		time.sleep(1)
		self.i2c_address = (0b0101000 | 0b010) # JP8 on HAT board
		self.spi = L6470Sc18is602bInterface(self.i2c, self.i2c_address)
		self.filter = Filter(self.spi)

		logger.info('Filter Homing start...')
		self.filter.release_switch() # release switch
		self.filter.go_until() # Go Home
		while self.filter.wait(): # Wait Go to Home
			time.sleep(0.01)
		logger.info('Filter Homing done.')

		self.positions = [0.0, 90.0, 180.0, 270.0]
		self.shotCounter = 0
		self.currentCycle = 0
		self.filterIndex = 0
		self.filterRunning = False
		self.isFilterActionFinished = True
		
		self.filters = { filterString : { "use" : False, 'ct' : "", 'name' : "" } for idx, filterString in enumerate(['FAM', 'HEX', 'ROX', 'CY5'])}

		# load recent protocol first
		defaultProtocol = [{"label":"1", "temp":95, "time":5},{"label":"2", "temp":95, "time":5},{"label":"3", "temp":55, "time":5},{"label":"4", "temp":72, "time":5},{"label":"GOTO", "temp":2, "time":4},{"label":"5", "temp":72, "time":5}]
		self.protocol = [Action(**action) for action in defaultProtocol]
		self.protocolName = 'Default Protocol'

		self.calcLeftTime()



	def initValues(self):
		self.currentCommand = Command.READY

		self.running = False
		self.completePCR = False
		self.targetArrival = False
		self.targetArrivalFlag = False
		self.targetArrivalDelta = 0.5
		self.freeRunning = False
		self.freeRunningCounter = 0

		# Timed Loop params
		self.leftSec = 0				# current action remain time
		self.leftTotalSec = 0			# total remain time
		self.currentActionNumber = -1	# current action number
		self.totalActionNumber = 0		# total action number
		self.leftGotoCount = -1			# remain goto count
		self.startTime = None			# pcr start time
		self.elapsedTime = ''			# 

		self.prevTargetTemp = 25.0
		self.currentTargetTemp = 25.0

		self.targetArrival = False
		self.targetArrivalFlag = False
		self.freeRunning = False
		self.freeRunningCounter = 0

		self.leftSec = 0
		self.leftTotalSec = 0
		self.currentActionNumber = -1
		self.state = State.READY
		self.stateString = 'idle'
		self.leftGotoCount = -1

		self.currentError = 0
		
		self.shotCounter = 0
		self.currentCycle = 0
		self.filterIndex = 0
		self.filterRunning = False
		self.isFilterActionFinished = True

		# Detection params 
		self.leds = { 'FAM' : 1, 'HEX' : 1, 'ROX' : 1, 'CY5' : 1 } # turn off : 1, turn on : 0
		self.led_control = 1					# led control param
		self.leds_pwm = [0] * 4					# leds pwm param
		# self.leds_pwm = [255] * 4		

		logger.info('Filter Homing start...')
		self.filter.release_switch() # release switch
		self.filter.go_until() # Go Home
		while self.filter.wait(): # Wait Go to Home
			time.sleep(0.01)
		logger.info('Filter Homing done.')
		self.calcLeftTime()
	
	def processCleanpPCR(self):
		self.initValues()
		# This value for notification on this function, not used yet.
		self.currentCommand = Command.PCR_STOP

	def updateProtocol(self, protocolData):
		self.protocolName 		= protocolData[0]
		self.filters 			= protocolData[1]
		# self.filterNames 		= protocolData[2]
		# self.filterCts 			= protocolData[3]
		# self.protocol 			= protocolData[4]
		self.protocol 			= [Action(**action) for action in protocolData[2]]
		self.initValues()
		
	def startPCR(self):
		logger.info('start PCR')
		self.initValues()
		self.currentTargetTemp = int(self.protocol[0].temp)
		self.photodiodes = [[], [], [], []]

		self.running = True
		self.currentCommand = Command.PCR_RUN
		self.startTime = datetime.now()
	
	def stopPCR(self):
		logger.info('Stop PCR...')
		self.processCleanpPCR()

	def find_pid(self):
		if fabs(self.prevTargetTemp - self.currentTargetTemp) < .5:
			return
		dist = 10000
		index = 0

		for idx, pid in enumerate(self.pids):
			tmp = fabs(self.prevTargetTemp - pid['start_temp']) + fabs(self.currentTargetTemp - pid['target_temp'])
			if tmp < dist:
				dist = tmp
				index = idx
		self.pid = self.pids[index]

	def getStatus(self):
		return {
			'running' 				: self.running,
			'state'					: int(self.state),
			'temperature'			: self.currentTemp,
			'remainingTotalSec'		: self.leftTotalSec,
			'remainingGotoCount'	: self.leftGotoCount,
			'currentActionNumber'	: self.currentActionNumber,
			'totalActionNumber'		: self.totalActionNumber,
			'completePCR'			: self.completePCR,
			'photodiodes'			: self.photodiodes,
			'serialNumber'			: self.serial_number
		}

	# maybe 50ms?
	def fast_loop(self):
		# Update tx buffer params
		tx = self.txBuffer
		tx.cmd 					= self.currentCommand
		tx.currentTargetTemp 	= self.currentTargetTemp
		
		tx.startTemp  			= self.pid['start_temp']
		tx.targetTemp 			= self.pid['target_temp']
		tx.Kp 					= self.pid['Kp']
		tx.Ki 					= self.pid['Ki']
		tx.Kd 					= self.pid['Kd']
		tx.integralMax			= self.integralMax

		tx.ledControl			= True
		# tx.led_wg				= self.leds[2] # ROX
		# tx.led_r				= self.leds[3] # CY5
		# tx.led_g				= self.leds[1] # HEX
		# tx.led_b				= self.leds[0] # FAM
		
		tx.led_wg				= self.leds['HEX'] # ROX
		tx.led_r				= self.leds['CY5'] # CY5
		tx.led_g				= self.leds['ROX'] # HEX
		tx.led_b				= self.leds['FAM'] # FAM
		
		tx.led_wg_pwm			= self.leds_pwm[2]
		tx.led_r_pwm			= self.leds_pwm[3]
		tx.led_g_pwm			= self.leds_pwm[1]
		tx.led_b_pwm			= self.leds_pwm[0]

		tx.compensation 		= self.compensation
		tx.currentCycle 		= self.currentCycle

		# Write tx buffer (65 bytes)
		self.device.write(tx.toBytes())

		# Read received data buffer (64 bytes)
		ReceivedDataBuffer = self.device.read(65)

		# copy rx buffer
		self.rxBuffer.setParams(ReceivedDataBuffer)

		# Update rx buffer params
		rx = self.rxBuffer
		self.state  			= rx.state
		# self.chamber = rx.chamber 
		self.currentTemp 		= rx.temperature
		self.currentPhotodiode 	= rx.photodiode
		self.requestData 		= rx.requestData
		self.currentError 		= rx.currentError

		if self.state == State.RUNNING:
			self.running = True

		self.check_error()
		if not self.running: return 

		self.free_running()
		self.check_target_temperature_arrival()
		
 
		
	def run(self):
		usbTimer = time.time()
		roundTimer = time.time()
		duration = round(TIMER_DURATION / 1000, 2)
		temp_command = self.currentCommand
		temp_state = self.state
		while True:
			currentTime = time.time()
			
			# USB Task (50 millesecond timer)
			if currentTime - usbTimer >= duration:
				# reset the usb task timer 
				usbTimer = time.time()
				self.fast_loop()

			# Real-time PCR Task (1000 millesecond timer)
			if currentTime - roundTimer >= 1:
				# reset the timer 
				roundTimer = time.time()
				logger.info(f'TEMP : {self.currentTemp}')

				if self.running:
					if self.run_protocol():
						continue
				if self.currentCommand == Command.PCR_STOP and self.state == State.READY:
					self.currentCommand = Command.READY
					self.stateString = 'idle'

	def run_protocol(self):
		self.elapsedTime = self._calc_elapsed_time()

		# ended current action
		if self.leftSec <= 0:
			return self.run_next_action()
				
		else: # the action is running now.
			self.wait_action_running()
			return False
		

	def run_next_action(self):
		self.currentActionNumber += 1
		logger.info(f'Action {self.currentActionNumber}/{self.totalActionNumber}')

		if self.currentActionNumber >= self.totalActionNumber:
			logger.info('End of protocol.')
			self.completePCR = True
			
			self.processCleanpPCR()
			return True

		action = self.protocol[self.currentActionNumber]
		if action.label == 'GOTO': # GOTO Label
			self.run_goto_action(action)

		elif action.label == 'SHOT': # SHOT Label
			self.run_shot_action()
		else: 
			self.run_heating_action(action)
		return False
	
	def run_goto_action(self, action:Action):
		if self.leftGotoCount < 0 :
			self.leftGotoCount = int(action.time)

		if self.leftGotoCount == 0:
			logger.info('GOTO ended!')
			self.leftGotoCount = -1
		else:
			self.leftGotoCount -= 1 
			targetActionLabel = f'{int(action.temp)}'
			logger.info(f'Check goto target label, left gotocount {self.leftGotoCount}, target : {targetActionLabel}')
			for i in range(self.currentActionNumber):
				if targetActionLabel == self.protocol[i].label:
					# The action number will increase, so decrease -1 idx first.
					self.currentActionNumber = i -1 
					logger.info(f'Target GOTO label found, {self.currentActionNumber}')
					break

	def run_shot_action(self):
		filterString = ['FAM', 'HEX', 'ROX', 'CY5']

		# check current filter index
		for idx, key in enumerate(self.filters):
			if self.filterIndex == idx and not self.filters[key]['use']:
				self.filterIndex = idx+1

		# 4 is finished
		if self.filterIndex == 4:
			self.filterIndex = 0
			self.currentCycle += 1
			self.filterRunning = False
			self.filter.position(self.positions[0])
			logger.info('shot action done...')
		
		# Run the filter
		else:
			if self.filterRunning:
				# isFilterActionFinished : motor moving is done.
				self.isFilterActionFinished = not self.filter.wait()
				
				if self.isFilterActionFinished:
					photodiode = self.currentPhotodiode

					# turn on the led, save the result and turn off the led.
					self.leds[filterString[self.filterIndex]] = 0
					
					self.shotCounter += 1
					if self.shotCounter >= 2:
						# save the filter data
						self.photodiodes[self.filterIndex].append(photodiode)
						logger.info(f'{self.currentCycle} Save the filter data - {self.filterIndex} : {self.currentPhotodiode}')
						
						# led turn off
						self.leds[filterString[self.filterIndex]] = 1
						self.shotCounter = 0

						# next filter
						self.filterIndex += 1
						self.filterRunning = False
			else:
				logger.info('filterwheel running...')
				self.filterRunning = True
				self.filter.position(self.positions[self.filterIndex])
			self.currentActionNumber -= 1

	def run_heating_action(self, action:Action):
		logger.info(f'current action is {action}')
		self.prevTargetTemp = self.currentTargetTemp
		self.currentTargetTemp = action.temp

		self.targetArrivalFlag = self.prevTargetTemp > self.currentTargetTemp

		self.targetArrival = False
		self.leftSec = int(action.time)

		self.find_pid()
	def wait_action_running(self):
		if not self.targetArrival:
			# logger.info('Not target arrived.')
			# TODO : Error (target temperature not arrival, counter base check logic)
			pass
		else:
			# Just decrease the left seconds
			self.leftSec -= 1
			self.leftTotalSec -= 1
			# logger.info(f'left time {self.leftSec}/{self.leftTotalSec}') 

	def check_error(self):
		error = False
		errorMessage = ''
		if self.currentError == Error.ERROR_ASSERT and not error:
			error = True
			errorMessage = 'Software error occured! \nPlease contact to developer'
		elif self.currentError == Error.ERROR_OVERHEAT and not error:
			error = True
			emergencyStop = True
			errorMessage = 'OverHeat error occured! \nPlease check the pcr chip or device!'
		return error, errorMessage
	
	def free_running(self):
		if self.targetArrivalFlag and not self.freeRunning:
			if self.currentTemp <= self.currentTargetTemp:
				logger.info('FreeRunning Start')
				self.freeRunning = True
				self.freeRunningCounter = 0
		
		if self.freeRunning:
			self.freeRunningCounter	+= 1

			# Check 3 second 
			if self.freeRunningCounter >= (3000 / TIMER_DURATION) :
				self.targetArrivalFlag = False
				self.freeRunning = False
				self.freeRunningCounter = 0
				self.targetArrival = True

	def check_target_temperature_arrival(self):
		# Target arrived check
		if fabs(self.currentTemp - self.currentTargetTemp) < self.targetArrivalDelta and (not self.targetArrivalFlag):
			self.targetArrival = True

	def calcLeftTime(self):
		# Calculate the protocol left time
		self.totalActionNumber = len(self.protocol)
		for idx, action in enumerate(self.protocol):

			if action.label == 'GOTO':
				targetLabel = str(int(action.temp))
				gotoIdx = -1
				for idx2, tempAction in enumerate(self.protocol):
					# checkLabel = tempAction.label
					if targetLabel == tempAction.label:
						gotoIdx = idx2
						break
				if gotoIdx != -1:
					tempTime = 0
					for i in range(gotoIdx, idx):
						tempTime += int(self.protocol[i].time)
					tempTime *= action.time
					self.leftTotalSec += tempTime
			elif action.label != 'SHOT':
				self.leftTotalSec += int(action.time)

	def _calc_elapsed_time(self):
		if not self.startTime:
			return ''
		elapsedTimeSec = (datetime.now() - self.startTime).total_seconds()
		mins, secs = divmod(elapsedTimeSec, 60)
		hours, mins = divmod(mins, 60)
		return '%02d:%02d:%02d' % (hours, mins, secs)

	
controller = Controller()
controller.start()			

context = zmq.Context()
listener = context.socket(zmq.REP)
listener.bind(f'tcp://*:{PCR_PORT}')

def command_handler(recv_data:dict):
	# Information
	if len(recv_data) == 0:
		return controller.getStatus()
	# For GUI display information
	# return the controller's status information
	
	command = recv_data['command']

	# Action Event
	response = { 'result' : False }

	if command == 'start': # Start PCR  
		if controller.running:
			response['reason'] = 'PCR is running'
		elif not recv_data.get('protocolData'):
				response['reason'] = 'protocol data is not valid'
		else:
			controller.photodiodes = [[], [], [], []]
			controller.updateProtocol(recv_data['protocolData'])
			controller.startPCR()
			response['result'] = True

	elif command == 'update':
		if controller.running:
			response['reason'] = 'PCR is running'
		elif not recv_data.get('protocolData'):
			response['reason'] = 'protocol data is not valid'
		else:
			logger.info('Protocol Start!!!')
			controller.photodiodes = [[], [], [], []]
			controller.updateProtocol(recv_data['protocolData'])
			response['result'] = True

	elif command == 'stop': # Stop PCR 
		if not controller.running:
			response['reason'] = 'PCR is not running'
		else:
			logger.info('Protocol Stop')
			controller.stopPCR()
			response['result'] = True
	else:
		response['reason'] = 'command is not valid'
	
	return response


if __name__ == '__main__':
	while True:
		try:
			recv_data = listener.recv_json()
		except Exception as e:
			logger.error(e)
			continue		
			
		response = command_handler(recv_data)
		listener.send_json(response)


	
