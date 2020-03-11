# -*- coding: utf-8 -*-
# api.py

from flask import Blueprint
from flask_restful import Api

from api.pcr import pcr
from api.pcr import protocol as pcrProtocol
from api.history import history as pcrHistory

# list of PCR api
bp_pcr = Blueprint('api_pcr', __name__)
bp_pcr_protocol = Blueprint('api_pcr_protocol', __name__)
bp_history = Blueprint('api_history', __name__)

# For PCR API
api_pcr = Api(bp_pcr)

api_pcr.add_resource(pcr.Start, '/start')
api_pcr.add_resource(pcr.Stop, '/stop')
api_pcr.add_resource(pcr.Status, '/status')
api_pcr.add_resource(pcr.ReloadProtocol, '/reloadProtocol')


# For PCR Protocol Api
api_pcr_protocol = Api(bp_pcr_protocol)
api_pcr_protocol.add_resource(pcrProtocol.ProtocolList, '/list')
api_pcr_protocol.add_resource(pcrProtocol.ProtocolSelect, '/select')
api_pcr_protocol.add_resource(pcrProtocol.NewProtocol, '/new')
api_pcr_protocol.add_resource(pcrProtocol.DeleteProtocol, '/delete')
api_pcr_protocol.add_resource(pcrProtocol.EditProtocol, '/edit')
api_pcr_protocol.add_resource(pcrProtocol.CheckProtocol, '/check')

# For history API
api_history = Api(bp_history)
api_history.add_resource(pcrHistory.HistoryList, '/list')
api_history.add_resource(pcrHistory.HistoryGraphData, '/graphdata')
api_history.add_resource(pcrHistory.HistoryTempData, '/tempdata')
