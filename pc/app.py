# main_server.py
# -*- coding: utf-8 -*-

from flask import Flask
from api import api as bp

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

"""
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
"""

if __name__ == '__main__':
    # Initialize the flask server
    app = Flask(__name__)
    app.register_blueprint(bp.bp_pcr, url_prefix='/api/pcr')
    app.run(host='localhost', port=6009, debug=True, use_reloader=False)
