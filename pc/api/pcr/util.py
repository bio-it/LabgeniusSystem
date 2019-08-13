# -*- coding: utf-8 -*-

import pickle
import logging
import sqlite3 as db
import json

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def getRecentProtocol():
	# default protocol
	defaultProtocol = [{"label":"1", "temp":95.0, "time":10},{"label":"2", "temp":95.0, "time":5},{"label":"3", "temp":55.0, "time":5},{"label":"4", "temp":72.0, "time":5},{"label":"GOTO", "temp":2.0, "time":4},{"label":"5", "temp":72.0, "time":5}]

	try:
		with open('database.prop', 'rb') as f:
			protocolName = pickle.load(f)	# line by line
			filters = pickle.load(f)
			protocol = pickle.load(f)

			# save to list data
			protocol = json.loads(protocol)
	except Exception as e:
		logger.info(str(e))
		# Load the first protocol and setting the default protocol
		logger.info("No recent protocol data.")

		protocolList = getProtocolList()

		# No protocol list on the database, make new protocol
		if len(protocolList) == 0:
			protocolName = 'Default protocol'
			filters = 'FAM'
			protocol = defaultProtocol
			setRecentProtocol(protocolName, filters, json.dumps(defaultProtocol))
		else: # Load the first protocol.
			protocolName = protocolList[0][1]
			filters = protocolList[0][2]
			protocol = protocolList[0][4]
			setRecentProtocol(protocolName, filters, protocol)

			# save to list data
			protocol = json.loads(protocol)

	return (protocolName, filters, protocol)

def setRecentProtocol(name, filters, protocol):
	with open('database.prop', 'wb') as f:
		pickle.dump(name, f)
		pickle.dump(filters, f)
		pickle.dump(protocol, f)

# Protocol database
def getProtocolList():
	conn = db.connect('database.db')
	cursor = conn.execute('select * from protocols')
	data = cursor.fetchall()
	conn.close()
	return data

def insertNewProtocol(name, filters, protocol):
	conn = db.connect('database.db')
	conn.execute("insert into protocols (name, filters, protocol) values('%s', '%s', '%s')" % (name, filters, protocol))
	conn.commit()
	conn.close()

def getProtocol(idx):
	conn = db.connect('database.db')
	cursor = conn.execute('select * from protocols where id=%d' % idx)
	data = cursor.fetchall()
	conn.close()
	return data
