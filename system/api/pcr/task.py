
# For emulating
import threading
import time

import datetime

import logging
import zmq
import smbus

import os

from enum import IntEnum
import math
import json

from api import util

class State(IntEnum):
    READY = 0x00,
    RUNNING = 0x01,

class Command(IntEnum):
    READY = 0x00,
    PCR_RUN = 0x01,
    PCR_STOP = 0x02,
    FAN_ON = 0x03,
    FAN_OFF = 0x04

class Protocol():
    def __init__(self, label, temp, time):
        self.label = label
        self.temp = temp
        self.time = time

    def toDict(self):
        return {"label" : self.label, "temp" : self.temp, "time" : self.time}


# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting the file logger for PCR task
fileHandler = logging.FileHandler("pcr.log")
logger.addHandler(fileHandler)

logger.info("Logger started!")
# zmq setting
PCR_PORT = os.environ.get('PCR_PORT', '7001')


class PCRThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # Daemon is important
        self.daemon = True
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect('tcp://localhost:%s' % PCR_PORT)

        self.running = False
        self.currentCommand = Command.READY
        self.completePCR = False
        self.targetArrival = False
        self.targetArrivalFlag = False
        self.targetArrivalDelta = 0.5
        self.freeRunning = False
        self.freeRunningCounter = 0

        self.leftSec = 0
        self.leftTotalSec = 0
        self.currentActionNumber = -1
        self.totalActionNumber = 0
        self.state = State.READY
        self.stateString = 'idle'
        self.currentTemp = 20.0
        self.startTime = None

        self.leftGotoCount = -1
        self.prevTargetTemp = 25.0
        self.currentTargetTemp = 25.0

        # need to setup
        self.compensation = 30
        self.currentError = 0
        self.currentPhotodiode = 0
        self.photodiodes = [[], [], [], []]

        self.elapsedTime = ''
        self.totalActionNumber = 0

        self.serialNumber = ''

        # for filter
        self.filterIndex = 0
        self.currentCycle = 0
        self.filterRunning = False
        self.shotCounter = 0

        # load recent protocol first
        self.protocols = []
        self.magnetoProtocols = []

        protocolData = util.getRecentProtocol()
        self.protocolName = protocolData[0]
        self.filters = ["", "", "", ""]
        self.filterNames = ["", "", "", ""]
        self.filterCts = ["", "", "", ""]

        # filter string to list
        filterStrings = ['FAM', 'HEX', 'ROX', 'CY5']
        tempFilters = [x.strip() for x in protocolData[1].split(',')]
        tempFilterNames = [x.strip() for x in protocolData[2].split(',')]
        tempFilterCts = [x.strip() for x in protocolData[3].split(',')]

        idx2 = 0
        for idx, filterName in enumerate(filterStrings):
            # check this filter is used
            if filterName in tempFilters:
                self.filters[idx] = tempFilters[idx2]
                self.filterNames[idx] = tempFilterNames[idx2]
                self.filterCts[idx] = tempFilterCts[idx2]

                idx2 += 1

        # For history
        self.result = ["", "", "", ""]
        self.resultCts = ["", "", "", ""]
        self.tempLogger = []

        for protocol in protocolData[4]:
            self.protocols.append(Protocol(protocol['label'], float(protocol['temp']), int(protocol['time'])))

        self.magnetoProtocols = protocolData[5]

        logger.info(self.protocols)
        self.totalActionNumber = len(self.protocols)

        # Calculate the protocol left times
        for idx, protocol in enumerate(self.protocols):
            label = protocol.label
            time = protocol.time

            # Check label is 'GOTO' or not
            if label == 'GOTO':
                targetLabel = '%d' % protocol.temp
                gotoIdx = -1
                # Check out the label's idx
                for idx2, tempProtocol in enumerate(self.protocols):
                    checkLabel = tempProtocol.label

                    if checkLabel == targetLabel:
                        gotoIdx = idx2
                        break

                # find out GOTO idx
                if gotoIdx != -1:
                    # Calculate GOTO times
                    tempTime = 0
                    for i in range(gotoIdx, idx):
                        tempTime += self.protocols[i].time

                    tempTime *= time

                    self.leftTotalSec += tempTime
            else:
                if label != 'SHOT':
                    self.leftTotalSec += time

    # For getting the device status
    def run(self):
        roundTimer = time.time()
        while True:
            # Protocol task
            # Only check when the PCR is running and 1 sec
            currentTime = time.time()

            if currentTime - roundTimer >= 1:
                # reset the timer
                roundTimer = time.time()

                if self.running:
                    elapsedTimeSec = (datetime.datetime.now() - self.startTime).total_seconds()
                    mins, secs = divmod(elapsedTimeSec, 60)
                    hours, mins = divmod(mins, 60)
                    self.elapsedTime = '%02d:%02d:%02d' % (hours, mins, secs)

                    logger.info("Elapsed time : %s" % self.elapsedTime)

                    # Check the current time is over
                    if self.leftSec == 0:
                        self.currentActionNumber += 1

                        logger.info("Action %d/%d" % (self.currentActionNumber, self.totalActionNumber))

                        # End of all PCR protocol
                        if self.currentActionNumber >= self.totalActionNumber:
                            logger.info("End of protocol.")
                            self.completePCR = True

                            logger.info(result)
                            self.processCleanupPCR()
                            continue

                        # If current protocol is not GOTO label
                        if self.protocols[self.currentActionNumber].label != 'GOTO' and self.protocols[self.currentActionNumber].label != 'SHOT':
                            logger.info("Current protocol is not GOTO : %s " % self.protocols[self.currentActionNumber].label)
                            self.prevTargetTemp = self.currentTargetTemp
                            self.currentTargetTemp = self.protocols[self.currentActionNumber].temp

                            self.targetArrivalFlag = self.prevTargetTemp > self.currentTargetTemp

                            self.targetArrival = False
                            self.leftSec = int(self.protocols[self.currentActionNumber].time)

                            # Timeout...?
                        elif self.protocols[self.currentActionNumber].label == 'GOTO':   # GOTO label
                            if self.leftGotoCount < 0:
                                self.leftGotoCount = int(self.protocols[self.currentActionNumber].time)

                            logger.info("Goto label, left goto count : %d" % self.leftGotoCount)

                            if self.leftGotoCount == 0:
                                logger.info("GOTO ended!")
                                self.leftGotoCount = -1
                            else:
                                self.leftGotoCount -= 1

                                # Changed to GOTO label for action number
                                targetActionLabel = '%d' % int(self.protocols[self.currentActionNumber].temp)
                                logger.info("Check goto target label, left gotocount : %d, target : %s" % (self.leftGotoCount, targetActionLabel))
                                for i in range(0, self.currentActionNumber):
                                    if targetActionLabel == self.protocols[i].label:
                                        # The action number will increase, so decrease -1 idx first.
                                        self.currentActionNumber = i-1
                                        logger.info("Target GOTO label found, %d" % self.currentActionNumber)
                                        break
                        else:   # SHOT label
                            print(self.filters)

                            # Check current filter
                            filters = ['FAM', 'HEX', 'ROX', 'CY5']

                            for idx, filterName in enumerate(filters):
                                if self.filterIndex == idx:
                                    # check this filter is used
                                    if not filterName in self.filters:
                                        self.filterIndex = idx+1

                            # 4 is last filter
                            if self.filterIndex == 4:
                                self.filterIndex = 0
                                self.currentCycle += 1

                                # if need to save the log, write here
                            else: # in progress
                                if self.filterRunning:
                                    # TODO: Check the motor moving is done.

                                    # turn on the led, save the result and turn off the led
                                    self.shotCounter += 1
                                    if self.shotCounter >= 2:
                                        # save the filter data
                                        self.photodiodes[self.filterIndex].append(self.currentPhotodiode)

                                        # save the filter data
                                        logger.info("Save the filter data[%d] : %d" % (self.filterIndex, self.currentPhotodiode))

                                        self.shotCounter = 0

                                        # next filter
                                        self.filterIndex += 1
                                        self.filterRunning = False
                                else:
                                    self.filterRunning = True
                                    # Run the motor

                                # retry the SHOT command
                                self.currentActionNumber -= 1

                    else:   # the action is running now.
                        if not self.targetArrival:   # not yet arrived the target temperature.
                            # for timeout routine, currently ignore it.
                            logger.info("Not target arrived")
                            pass
                        else: # only target is arrived
                            # Just decrease the left seconds
                            self.leftSec -= 1
                            self.leftTotalSec -= 1
                            logger.info("left time %d/%d" % (self.leftSec, self.leftTotalSec))


                    # Check freeRunning
                    if self.targetArrivalFlag and not self.freeRunning:
                        if self.currentTemp <= self.currentTargetTemp:
                            logger.info("FreeRunning True!")
                            self.freeRunning = True
                            self.freeRunningCounter = 0

                    if self.freeRunning:
                        self.freeRunningCounter += 1
                        logger.info("Free running counter : %d" % self.freeRunningCounter)

                        # Check 3 second
                        if self.freeRunningCounter >= 3:
                            logger.info("FreeRunning ended & target arrived")
                            self.targetArrivalFlag = False
                            self.freeRunning = False
                            self.freeRunningCounter = 0
                            self.targetArrival = True

                    # Target arrived check
                    if math.fabs(self.currentTemp-self.currentTargetTemp) < self.targetArrivalDelta and not self.targetArrivalFlag:
                        logger.info("Target arrivived checked")
                        self.targetArrival = True


            self.client.send_json({"cmd":self.currentCommand, "currentTargetTemp":self.currentTargetTemp, "ledControl":1, "led_wg":0, "led_r":0, "led_g":0, "led_b":0, "compensation":self.compensation})
            result = self.client.recv_json()

            # Save the information into member variables.
            self.currentTemp = float(result["temp"])
            self.state = result["state"]
            self.currentError = result["currentError"]
            self.currentPhotodiode = result["photodiode"]
            self.serialNumber = result["serialNumber"]

            if self.state == State.RUNNING:
                stateString = 'PCR in progress'

            if self.running:
                self.tempLogger.append("%d\t%.1f" % (len(self.tempLogger), self.currentTemp))

            # Check the state
            if self.currentCommand == Command.PCR_STOP and self.state == State.READY:
                self.currentCommand = Command.READY
                self.stateString = 'idle'

            # 50 millesecond but almost take 100ms
            time.sleep(0.05)

    def initValues(self):
        self.targetArrival = False
        self.targetArrivalFlag = False
        self.freeRunning = False
        self.freeRunningCounter = 0

        self.leftSec = 0
        self.leftTotalSec = 0
        self.currentActionNumber = -1
        self.currentCycle = 0
        self.state = State.READY
        self.stateString = 'idle'
        self.startTime = None
        self.leftGotoCount = -1

        self.prevTargetTemp = 25.0
        self.currentTargetTemp = 25.0

        self.elapsedTime = ''
        self.currentError = 0
        self.currentPhotodiode = 0
        self.photodiodes = [[], [], [], []]

        # for filter
        self.filterIndex = 0
        self.currentCycle = 0
        self.filterRunning = False

        # load recent protocol first
        self.protocols = []
        self.magnetoProtocols = []

        protocolData = util.getRecentProtocol()
        self.protocolName = protocolData[0]
        self.filters = ["", "", "", ""]
        self.filterNames = ["", "", "", ""]
        self.filterCts = ["", "", "", ""]

        # filter string to list
        filterStrings = ['FAM', 'HEX', 'ROX', 'CY5']
        tempFilters = [x.strip() for x in protocolData[1].split(',')]
        tempFilterNames = [x.strip() for x in protocolData[2].split(',')]
        tempFilterCts = [x.strip() for x in protocolData[3].split(',')]

        idx2 = 0
        for idx, filterName in enumerate(filterStrings):
            # check this filter is used
            if filterName in tempFilters:
                self.filters[idx] = tempFilters[idx2]
                self.filterNames[idx] = tempFilterNames[idx2]
                self.filterCts[idx] = tempFilterCts[idx2]

                idx2 += 1

        for protocol in protocolData[4]:
            self.protocols.append(Protocol(protocol['label'], float(protocol['temp']), int(protocol['time'])))

        self.magnetoProtocols = protocolData[5]

        # For history
        self.result = ["", "", "", ""]
        self.resultCts = ["", "", "", ""]
        self.tempLogger = []

        logger.info(self.protocols)

        self.totalActionNumber = len(self.protocols)

        # Calculate the protocol left times
        for idx, protocol in enumerate(self.protocols):
            label = protocol.label
            time = protocol.time

            # Check label is 'GOTO' or not
            if label == 'GOTO':
                targetLabel = '%d' % protocol.temp
                gotoIdx = -1
                # Check out the label's idx
                for idx2, tempProtocol in enumerate(self.protocols):
                    checkLabel = tempProtocol.label

                    if checkLabel == targetLabel:
                        gotoIdx = idx2
                        break

                # find out GOTO idx
                if gotoIdx != -1:
                    # Calculate GOTO times
                    tempTime = 0
                    for i in range(gotoIdx, idx):
                        tempTime += self.protocols[i].time

                    tempTime *= time

                    self.leftTotalSec += tempTime
            else:
                if label != 'SHOT':
                    self.leftTotalSec += time

    def startPCR(self):
        logger.info("called start")

        # Check the current state of PCR, and start or error
        # Currently, just start the PCR.
        self.initValues()
        self.startTime = datetime.datetime.now()
        self.currentTargetTemp = self.protocols[0].temp

        self.running = True
        self.currentCommand = Command.PCR_RUN

    def stopPCR(self):
        self.processCleanupPCR()

    def getStatus(self):
        protocols = [protocol.toDict() for protocol in self.protocols]

        data = {
            "running" : self.running,
            "state" : int(self.state),
            "stateString" : self.stateString,
            "temperature" : self.currentTemp,
            "remainingSec" : self.leftSec,
            "remainingTotalSec" : self.leftTotalSec,
            "remainingGotoCount" : self.leftGotoCount,
            "currentActionNumber" : self.currentActionNumber,
            "totalActionNumber" : self.totalActionNumber,
            "elapsedTime" : self.elapsedTime,
            "protocols" : protocols,
            "magnetoProtocols" : self.magnetoProtocols,
            "protocolName" : self.protocolName,
            "filters" : self.filters,
            "filterNames" : self.filterNames,
            "filterCts" : self.filterCts,
            "result" : self.result,
            "resultCts" : self.resultCts,
            "serialNumber" : self.serialNumber,
            "photodiodes" : self.photodiodes
        }
        # For GUI display information.
        # Return the status information.
        return data

    # internal protocol
    def reloadProtocol(self):
        if self.running:
            return False

        # reload the protocol
        self.initValues()
        return True

    def isRunning(self):
        return self.running

    def processCleanupPCR(self):
        # Check the complete the PCR for saving the history
        if self.completePCR:
            # save the history
            # need to change the timedelta for utc+9 now, when the internet connection is established, don't use this timedelta function.
            currentDate = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
            target = json.dumps(self.filterNames)
            filterData = json.dumps(self.filters)
            ct = json.dumps(self.resultCts)
            result = json.dumps(self.result)
            graphData = json.dumps(self.photodiodes)
            tempData = json.dumps(self.tempLogger)
            logger.info("history saved!")

            util.saveHistory(currentDate, target, filterData, ct, result, graphData, tempData)


        self.initValues()
        self.running = False
        # This value for notification on this function, not used yet.
        self.completePCR = False
        self.currentCommand = Command.PCR_STOP
