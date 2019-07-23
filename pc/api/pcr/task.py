
# For emulating
import threading
import time

import datetime

import logging
import zmq

from enum import Enum
import math

class State(Enum):
    READY = 0x00,
    RUNNING = 0x01,
    ERROR = 0x02,

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
PCR_PORT = 6060

# For emulating PCR
# Send message to zmq server for getting temperature data.
#
class PCRThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # Daemon is important
        self.daemon = True
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect('tcp://localhost:%d' % PCR_PORT)

        self.running = False
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
        self.currentTemp = 20.0
        self.startTime = None

        self.leftGotoCount = -1
        self.prevTargetTemp = 25.0
        self.currentTargetTemp = 25.0

        self.elapsedTime = ''

        logger.info('initialize..')

        # Initialize emulator protocols
        # No check protocol parsing error now.
        self.protocols = []
        self.protocols.append(Protocol('1', 95.0, 10))
        self.protocols.append(Protocol('2', 95.0, 5))
        self.protocols.append(Protocol('3', 55.0, 5))
        self.protocols.append(Protocol('4', 72.0, 5))
        self.protocols.append(Protocol('GOTO', 2.0, 4))
        self.protocols.append(Protocol('5', 72.0, 5))

        # Total protocol number
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
                self.leftTotalSec += time

    # For getting the device status
    def run(self):
        while True:
            # Protocol task
            # Only check when the PCR is running.
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
                        self.processCleanupPCR()
                        continue

                    # If current protocol is not GOTO label
                    if self.protocols[self.currentActionNumber].label != 'GOTO':
                        logger.info("Current protocol is not GOTO : %s " % self.protocols[self.currentActionNumber].label)
                        self.prevTargetTemp = self.currentTargetTemp
                        self.currentTargetTemp = self.protocols[self.currentActionNumber].temp

                        self.targetArrivalFlag = self.prevTargetTemp > self.currentTargetTemp

                        self.targetArrival = False
                        self.leftSec = int(self.protocols[self.currentActionNumber].time)

                        # Send to time setting command
                        self.client.send_json({"command":"T", "targetTemp":self.currentTargetTemp})
                        result = self.client.recv_json()

                        logger.info("Target temp setting command sent")
                        logger.info(result)

                        # Timeout...?
                    else:   # GOTO label
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

            self.client.send_json({"command":"C"})
            result = self.client.recv_json()

            # Save the information into member variables.
            self.currentTemp = float(result["temp"])
            logger.info(result)

            # 1 second
            time.sleep(1)



    def initValues(self):
        self.targetArrival = False
        self.targetArrivalFlag = False
        self.freeRunning = False
        self.freeRunningCounter = 0

        self.leftSec = 0
        self.leftTotalSec = 0
        self.currentActionNumber = -1
        self.state = State.READY
        self.startTime = None
        self.leftGotoCount = -1

        self.prevTargetTemp = 25.0
        self.currentTargetTemp = 25.0

        self.elapsedTime = ''

        # For emulator only
        self.totalActionNumber = len(self.protocols)

        # For emulator only
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
                self.leftTotalSec += time

    def startPCR(self):
        logger.info("called start")

        # Check the current state of PCR, and start or error
        # Currently, just start the PCR.
        self.initValues()
        self.startTime = datetime.datetime.now()
        currentTargetTemp = self.protocols[0].temp

        self.running = True
        self.state = State.RUNNING

    def stopPCR(self):
        self.processCleanupPCR()

    def getStatus(self):
        # protocols = [protocol.toDict() for protocol in self.protocols]

        data = {
            "running" : self.running,
            "state" : int(self.state.value),
            "temperature" : self.currentTemp,
            "remainingSec" : self.leftSec,
            "remainingTotalSec" : self.leftTotalSec,
            "remainingGotoCount" : self.leftGotoCount,
            "currentActionNumber" : self.currentActionNumber,
            "totalActionNumber" : self.totalActionNumber,
            "elapsedTime" : self.elapsedTime,
        }
        # For GUI display information.
        # Return the status information.
        return data

    # not yet confirmed
    def setProtocol(self):
        pass

    def isRunning(self):
        return self.running

    def processCleanupPCR(self):
        self.initValues()
        self.running = False
        # This value for notification on this function, not used yet.
        self.completePCR = False
        self.state = State.READY
