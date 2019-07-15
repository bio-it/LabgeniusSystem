
# For emulating
import threading
import time

import logging
import zmq

from enum import Enum

class State(Enum):
    READY = 0x00,
    HEATING = 0x01,
    ERROR = 0x02,

class Protocol():
    def __init__(self, label, temp, time):
        self.label = label
        self.temp = temp
        self.time = time

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# zmq setting
PCR_PORT = 6060

# For emulating PCR
# Send message to zmq server for getting temperature data.
#
class PCRThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect('tcp://localhost:%d' % PCR_PORT)

        self.running = False
        self.completePCR = False
        self.targetArrival = False
        self.leftSec = 0
        self.leftTotalSec = 0
        self.currentActionNumber = -1
        self.totalActionNumber = 0
        self.state = State.READY

        # Initialize emulator protocols
        # No check protocol parsing error now.
        self.protocols = []
        self.protocols.append(Protocol('1', 95.0, 30))
        self.protocols.append(Protocol('2', 95.0, 30))
        self.protocols.append(Protocol('3', 55.0, 30))
        self.protocols.append(Protocol('4', 72.0, 30))
        self.protocols.append(Protocol('GOTO', 2.0, 10))
        self.protocols.append(Protocol('5', 72.0, 30))

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
            self.client.send_json({"command":"C"})
            result = self.client.recv_json()

            # Save the information into member variables.

            logger.info(result)

            # 1 second
            time.sleep(1)

    def startPCR(self):
        logger.info("called start")

    def getStatus(self):
        pass

    def stopPCR(self):
        pass

    # not yet confirmed
    def setProtocol(self):
        pass

    def isRunning(self):
        return self.running

