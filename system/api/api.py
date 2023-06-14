# -*- coding: utf-8 -*-
# api.py

from flask import Blueprint
from flask_restful import Api

from api.task import task
from api.protocol import protocol 
from api.history import history as pcrHistory
from api.magneto import magneto


# list of PCR api
bp_task = Blueprint('api_task', __name__)
bp_protocol = Blueprint('api_protocol', __name__)
bp_history = Blueprint('api_history', __name__)
bp_magneto = Blueprint('api_magneto', __name__)


# For PCR API
api_task = Api(bp_task)

api_task.add_resource(task.Start, '/start')
api_task.add_resource(task.Stop, '/stop')
api_task.add_resource(task.Status, '/status')

# For PCR Protocol Api
api_protocol = Api(bp_protocol)
api_protocol.add_resource(protocol.ProtocolList, '/list')
api_protocol.add_resource(protocol.ProtocolSelect, '/select')
api_protocol.add_resource(protocol.CreateProtocol, '/create')
api_protocol.add_resource(protocol.EditProtocol, '/edit')
api_protocol.add_resource(protocol.DeleteProtocol, '/delete')
api_protocol.add_resource(protocol.CheckProtocol, '/check')
api_protocol.add_resource(protocol.ReloadProtocol, '/reload')

# For history API
api_history = Api(bp_history)
api_history.add_resource(pcrHistory.HistoryList, '/list')
api_history.add_resource(pcrHistory.HistoryGraphData, '/graphdata')
api_history.add_resource(pcrHistory.HistoryTempData, '/tempdata')

# For magneto API
api_magneto = Api(bp_magneto)
api_magneto.add_resource(magneto.Run, '/run')