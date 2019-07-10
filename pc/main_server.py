# main_server.py
# -*- coding: utf-8 -*-

from flask import Flask

import zmq

import threading
import time

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# For emulating PCR
class TaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.test = False

    def run(self):
        self.running = True
        while True:
            time.sleep(0.1)

    def isRunning(self):
        return self.running

    def setTest(self):
        self.test = True

    def getTest(self):
        return self.test

# For
class PCRManager():
    def __init__(self):
        self.context = zmq.Context()

        # For using the receive timeout
        # setsockopt(zmq.RCVTIMEO, 1000)
        # LINGER, 0
        self.client = self.context.socket(zmq.REQ)
        self.client.connect('tcp://localhost:6060')

    def sendStartTempControl(self, targetTemp):
        self.client.send_json({"command":"T", "targetTemp":targetTemp})

    def sendGetTemp(self):
        self.client.send_json({"command":"C"})
        result = self.client.recv_json()

        logger.info(result)
        return result

    def sendStopTempControl(self):
        self.client.send_json({"command":"S"})

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello world2'

@app.route('/start')
def tempControl():
    thread.setTest()
    pcrManager.sendStartTempControl(60.0)
    return 'ok'

@app.route('/temp')
def getTemp():
    result = pcrManager.sendGetTemp()
    logging.info(result)
    logging.info(thread.getTest())
    if result['result'] == "ok":
        return 'response from server : state - %s, temp - %s' % (result["state"], result["temp"])
    else:
        return 'response from server : %s' % (result["result"])

@app.route('/stop')
def stopTempControl():
    pcrManager.sendStopTempControl()
    return 'ok'

if __name__ == '__main__':
    logging.info("running")
    pcrManager = PCRManager()

    # For emulating the PCR task
    thread = TaskThread()
    thread.start()

    app.run(host='localhost', port=80, debug=True)
