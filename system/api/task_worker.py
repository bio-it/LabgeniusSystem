
# For emulating
import threading
import time

import datetime

import logging
import zmq
# import smbus

import os
import numpy as np
from enum import IntEnum
import json

from api import util
from UserDefs import State, Command, Action

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting the file logger for PCR task
# fileHandler = logging.FileHandler("pcr.log")
# logger.addHandler(fileHandler)

logger.info("Logger started!")

# zmq setting
PCR_PORT = os.environ.get('PCR_PORT', '7001')
MAGNETO_PORT = os.environ.get('MAGNETO_PORT', '7005')

MagnetoState = ["Washing 1...", "Washing 2...", "Elution...", "Lysis...", "Mixing..."]

# singletone pattern
class TaskWorker(threading.Thread):
    __instance = None
    
    @classmethod
    def _getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls.__instance

    def __init__(self):
        threading.Thread.__init__(self)
        # Daemon is important
        self.daemon = True

        # PCR ZMQ Socket initialize 
        self.context = zmq.Context()
        
        self.pcrClient = self.context.socket(zmq.REQ)
        self.pcrClient.connect('tcp://127.0.0.1:%s' % PCR_PORT)
        self.pcrMessage = { 'command' : 'none' }

        self.magnetoClient = self.context.socket(zmq.REQ)
        self.magnetoClient.connect('tcp://127.0.0.1:%s' % MAGNETO_PORT)

        # self.magnetoClient = self.context.socket(zmq.REQ)
        # self.magnetoClient.connect('tcp://localhost:%s' % MAGNETO_PORT)

        self.running = False
        self.currentCommand = Command.READY
        self.magnetoCommand = ''
        self.pcrCommand = {}

        self.state = State.READY
        self.stateString = 'idle'

        self.currentTemp = 25.0
        self.remainingTotalSec = 0
        self.remainingGotoCount = 0
        self.currentActionNumber = 0
        self.totalActionNumber = 0
        self.completePCR = False
        self.photodiodes = [[], [], [], []]
        self.serialNumber = ''

        # for history
        self.result = ['', '', '', '']
        self.resultCts = ['', '', '', '']
		
        # Magneto Params
        self.magnetoIndex = -1
        self.magnetoCounter = 0
        self.magnetoRunning = False
        self.magnetoWait = False

        # Protocol
        self.protocol = []
        self.magnetoProtocol = []
        
        protocolData = util.getRecentProtocol()
        self.protocolName = protocolData[0]
        self.filters = protocolData[1]

        # For history
        self.result = ["", "", "", ""]
        self.resultCts = ["", "", "", ""]
        self.tempLogger = []
        for action in protocolData[2]:
            self.protocol.append(Action(**action))
        
        self.magnetoProtocol = list(filter(lambda x:x, protocolData[3]))
        
    # For getting the device status
    def run(self):
        roundTimer = time.time()
        while True:
            currentTime = time.time()
            if currentTime - roundTimer >= 0.5: # 500ms timer
                roundTimer = time.time()
                self._update_magneto_data()
                self._update_pcr_data()

    def _update_magneto_data(self):
        command = self.magnetoCommand
        self.magnetoClient.send_string(command)
        resp = self.magnetoClient.recv_json()
        
        if not resp['result']:
            return False, resp['reason']
        
        logger.info(f'get_status {resp}')
        if len(command) == 0:
            self.magnetoWait = resp['data']['running']
            if self.currentCommand == Command.MAGNETO:
                self.stateString = resp['data']['runningCommand']

                if not self.magnetoWait:
                    logger.info('magneto done...')
                    self._finish_magneto_protocol()
        else:
            self.magnetoCommand = ''

        return True, ''
    def _update_pcr_data(self):
        # Update Status
        command = self.pcrCommand
        self.pcrClient.send_json(command)
        resp = self.pcrClient.recv_json()

        if len(command) != 0:
            self.pcrCommand.clear()
            return 
        
        completePCR = self.completePCR

        self.state = resp['state']
        self.running = resp['running']
        self.currentTemp = resp['temperature']
        self.remainingTotalSec = resp['remainingTotalSec']
        self.remainingGotoCount = resp['remainingGotoCount']
        self.currentActionNumber = resp['currentActionNumber']
        self.totalActionNumber = resp['totalActionNumber']
        self.completePCR = resp['completePCR']
        self.photodiodes = resp['photodiodes']
        self.serialNumber = resp['serialNumber']
        
        # For History
        if self.running:
            self.tempLogger.append(self.currentTemp)

        # check protocol is ended
        if self.completePCR and not completePCR:
            logger.info('Protocol is Done...')
            self.processCleanupPCR()
    def _finish_magneto_protocol(self):
        self.running = True
        self.magnetoRunning = False
        self.currentCommand = Command.PCR_RUN
        self.startTime = datetime.datetime.now()
        self.stateString = 'PCR in progress'

        protocol = list(map(lambda x : x.__dict__, self.protocol))
        protocolData = [self.protocolName, self.filters, protocol]
        self.pcrCommand = { 'command' : 'start', 'protocolData' : protocolData }

        # self.pcrClient.send_json(message)
        # response = self.pcrClient.recv_json()
    
    def initValues(self):
        self.running = False
        self.currentCommand = Command.READY
        
        self.state = State.READY
        self.stateString = 'idle'
        self.serialNumber = ''

        # Magneto Params
        self.magnetoIndex = -1
        self.magnetoCounter = 0
        self.magnetoRunning = False

        # Protocol
        self.protocol = []
        self.magnetoProtocol = []
        
        protocolData = util.getRecentProtocol()
        self.protocolName = protocolData[0]
        self.filters = protocolData[1]

        # For history
        self.result = ["", "", "", ""]
        self.resultCts = ["", "", "", ""]
        self.tempLogger = []
        for action in protocolData[2]:
            self.protocol.append(Action(**action))
        
        self.magnetoProtocol = list(filter(lambda x:x, protocolData[3]))

    def _start(self):
        self.result = ['', '', '', '']
        self.resultCts = ['', '', '', '']
        self.photodiodes = [[], [], [], []]
        self.startMagneto()

    def startMagneto(self):
        self.magnetoRunning = True
        self.currentCommand = Command.MAGNETO
        self.magnetoCommand = 'protocol_run ' + '\n'.join(self.magnetoProtocol)
    
    def startPCR(self):
        # for history
        self.result = ['', '', '', '']
        self.resultCts = ['', '', '', '']

        self.pcrMessage['command'] = 'start'
        protocol = list(map(lambda x : x.__dict__, self.protocol))
        protocolData = [self.protocolName, self.filters, protocol]
        self.pcrCommand = { 'command' : 'start', 'protocolData' : protocolData }

        # self.pcrClient.send_json(message)
        # response = self.pcrClient.recv_json()
    
    def stopMagneto(self):
        self.currentCommand = Command.READY
        self.magnetoRunning = False
        self.magnetoCommand = 'stop'

    def stopPCR(self):
        self.pcrCommand = { 'command' : 'stop'}
    
    def _stop(self):
        if not self.running:
            return False
        
        if self.currentCommand == Command.MAGNETO:
            self.stopMagneto()
        elif self.currentCommand == Command.PCR_RUN:
            self.stopPCR()

        return False

    def getStatus(self):
        filters = []
        filterNames = []
        filterCts = []
        for key, val in self.filters.items():
            if val['use']:
                filters.append(key)
                filterNames.append(val['name'])
                filterCts.append(val['ct'])
            else:
                filters.append('')
                filterNames.append('')
                filterCts.append('')
        return {
            'running' : self.isRunning(),
            'command' : self.currentCommand,
            'temperature' : round(self.currentTemp, 2),
            'state' : self.state,
            'stateString' : self.stateString,
            "filters" : filters,
            "filterNames" : filterNames,
            "filterCts" : filterCts,
            'remainingTotalSec' : self.remainingTotalSec,
            'remainingGotoCount' : self.remainingGotoCount,
            'currentActionNumber' : self.currentActionNumber,
            'photodiodes' : self.photodiodes,
            'completePCR' : self.completePCR,
            'serialNumber' : self.serialNumber,
            'result' : self.result,
            'resultCts' : self.resultCts,
            'protocolName' : self.protocolName,
            'protocol' : [action.__dict__ for action in self.protocol],
            'magnetoProtocol' : self.magnetoProtocol
        }

    # internal protocol
    def reloadProtocol(self):
        if self.running or self.magnetoRunning:
            return False

        # reload the protocol
        self.initValues()
        return True

    def isRunning(self):
        return self.running or self.magnetoRunning

    def calcCT(self, index, filterCt):
        resultText = "FAIL"
        ct = 0
        sensorValue = np.array(self.photodiodes[index])
        idx = sensorValue.size
        if sensorValue.size > 10:
            # change calculate CT value function
            base_mean = sensorValue[3:16].mean()

            threshold = 0.697 * 4000.0 / 10
            logThreshold = np.log(threshold)
            logValue = np.log(sensorValue - base_mean)
            logValue[logValue <= 0] = 0

            for i in range(logValue.size):
                if logValue[i] > logThreshold:
                    idx = i
                    break

            if not 0 < idx < logValue.size:
                resultText = "Not detected"
            else:
                cpos = idx + 1
                cval = logValue[idx]
                delta = cval - logValue[idx-1]
                cq = cpos - (cval - logThreshold) / delta
                resultText = "Negative" if filterCt <= cq else "Positive"

    
        self.result[index] = resultText
        self.resultCts[index] = round(cq, 2)

    def processCleanupPCR(self):
        self.tempLogger = []

        if self.state == State.READY:
            self.stateString = 'idle'
        
        filterData = []
        filterNames = []
        
        for index, key in enumerate(self.filters):
            if self.filters[key]['use']:
                filterData.append(key)
                filterNames.append(self.filters[key]['name'])

                self.calcCT(index, float(self.filters[key]['ct']))

        # save the history
        # need to change the timedelta for utc+9 now, when the internet connection is established, don't use this timedelta function.
        currentDate = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
        
        target = json.dumps(filterNames)
        filterData = json.dumps(filterData)
        ct = json.dumps(self.resultCts)

        result = json.dumps(self.result)
        graphData = json.dumps(self.photodiodes)
        tempData = json.dumps(self.tempLogger)
        logger.info("history saved!")

        util.saveHistory(currentDate, target, filterData, ct, result, graphData, tempData)
        # util.saveHistory(currentDate, target, filterData, ct, result, graphData, tempData)

        self.stopPCR()
