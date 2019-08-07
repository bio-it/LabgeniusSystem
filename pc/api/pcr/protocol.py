# -*- coding: utf-8 -*-

from flask_restful import Resource
import logging

from api.pcr import util

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolList(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		util.getProtocolList()

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

class ProtocolSelect(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		util.getRecentProtocol()

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

class NewProtocol(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		util.insertNewProtocol('test', "{\"test\":\"test\"}")

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

class DeleteProtocol(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

class EditProtocol(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

class CheckProtocol(Resource):
	def get(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200

	def post(self):
		# Check the current state first
		response = {
			'result' : 'ok'
		}

		return response, 200