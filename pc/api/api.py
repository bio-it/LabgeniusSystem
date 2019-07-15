# -*- coding: utf-8 -*-
# api.py

from flask import Blueprint
from flask_restful import Api

from api.pcr import pcr

# list of PCR api
bp_pcr = Blueprint('api_pcr', __name__)
api_pcr = Api(bp_pcr)
api_pcr.add_resource(pcr.Start, '/start')

