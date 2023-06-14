# -*- coding: utf-8 -*-
from flask_restful import Resource
from flask import request
# Member functions for pcr task
# from api.magneto import task
import logging
from magneto.magneto_task import MagnetoTask


import os
import zmq

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# create and start magneto task
magneto_task = MagnetoTask()
magneto_task.start()


class Run(Resource):
    def post(self):
        requestData = request.data
        requestData = requestData.decode('utf-8')
        # print(f'Run api:{requestData}')
        result, reason, data = magneto_task.run_command(requestData)
        if result:
            response = {'result': 'ok', 'reason': reason, 'data': data}
        else:
            response = {'result': 'fail', 'reason': reason, 'data': None}
        return response, 200

