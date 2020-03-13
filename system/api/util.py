# -*- coding: utf-8 -*-

import pickle
import logging
import sqlite3 as db
import json

import socket
import fcntl
import struct
import os

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def getEth0IpAddress():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', b'eth0'))[20:24])

def getRecentProtocol():
	# default protocol
	defaultProtocol = [{"label":"1", "temp":95.0, "time":10},{"label":"2", "temp":95.0, "time":5},{"label":"3", "temp":55.0, "time":5},{"label":"4", "temp":72.0, "time":5},{"label":"GOTO", "temp":2.0, "time":4},{"label":"5", "temp":72.0, "time":5}]
	defaultMagnetoProtocol = ["ready"]

	try:
		with open('database.prop', 'rb') as f:
			protocolName = pickle.load(f)	# line by line
			filters = pickle.load(f)
			filterNames = pickle.load(f)
			filterCts = pickle.load(f)
			protocol = pickle.load(f)
			magnetoProtocol = pickle.load(f)

			# save to list data
			protocol = json.loads(protocol)
			magnetoProtocol = json.loads(magnetoProtocol)
	except Exception as e:
		logger.info(str(e))
		# Load the first protocol and setting the default protocol
		logger.info("No recent protocol data.")

		protocolList = getProtocolList()

		# No protocol list on the database, make new protocol
		if len(protocolList) == 0:
			protocolName = 'Default protocol'
			filters = 'FAM'
			filterNames = 'CT'
			filterCts = '38.0'
			protocol = defaultProtocol
			magnetoProtocol = defaultMagnetoProtocol

		else: # Load the first protocol.
			protocolName = protocolList[0][1]
			filters = protocolList[0][2]
			filterNames = protocolList[0][3]
			filterCts = protocolList[0][4]
			protocol = protocolList[0][5]
			magnetoProtocol = protocolList[0][6]

			# save to list data
			protocol = json.loads(protocol)
			magnetoProtocol = json.loads(magnetoProtocol)

		setRecentProtocol(protocolName, filters, filterNames, filterCts, json.dumps(protocol), json.dumps(magnetoProtocol))

	return (protocolName, filters, filterNames, filterCts, protocol, magnetoProtocol)

def setRecentProtocol(name, filters, filterNames, filterCts, protocol, magnetoProtocol):
	with open('database.prop', 'wb') as f:
		pickle.dump(name, f)
		pickle.dump(filters, f)
		pickle.dump(filterNames, f)
		pickle.dump(filterCts, f)
		pickle.dump(protocol, f)
		pickle.dump(magnetoProtocol, f)

def clearRecentProtocol():
	if os.path.exists("database.prop"):
  		os.remove("database.prop")

# Protocol database
def getProtocolList():
	conn = db.connect('database.db')
	cursor = conn.execute('select id, name, filters, filter_names, filter_cts, protocol, magneto_protocol from protocols')
	data = cursor.fetchall()

	result = []
	for d in data:
		temp = {"id":d[0], "name":d[1], "filters":d[2], "filterNames":d[3], "filterCts":d[4], "protocol":d[5], "magnetoProtocol":d[6]}
		result.append(temp)

	conn.close()
	return result

def insertNewProtocol(name, filters, filterNames, filterCts, protocol, magnetoProtocol):
	conn = db.connect('database.db')
	conn.execute("insert into protocols (name, filters, filter_names, filter_cts, protocol, magneto_protocol) values('%s', '%s', '%s', '%s', '%s', '%s')" % (name, filters, filterNames, filterCts, protocol, magnetoProtocol))
	conn.commit()
	conn.close()

def checkProtocolExist(name):
	conn = db.connect('database.db')
	cursor = conn.execute('select name from protocols where name=%s' % name)
	data = cursor.fetchall()
	conn.close()

	if len(data) != 0:
		return True
	else:
		return False

def getProtocol(idx):
	conn = db.connect('database.db')
	cursor = conn.execute('select name, filters, filter_names, filter_cts, protocol, magneto_protocol from protocols where id=%d' % idx)
	data = cursor.fetchall()

	result = {}

	if len(data) == 1:
		result = {"name":data[0][0], "filters":data[0][1], "filterNames":data[0][2], "filterCts":data[0][3], "protocol":data[0][4], "magnetoProtocol":data[0][5]}

	conn.close()
	return result

def deleteProtocol(idx):
	conn = db.connect('database.db')
	cursor = conn.execute('delete from protocols where id=%d' % idx)
	result = cursor.rowcount == 1
	conn.commit()
	conn.close()

	return result

def editProtocol(idx, filters, filterNames, filter_cts, protocol, magnetoProtocol):
	conn = db.connect('database.db')
	cursor = conn.execute("update protocols set filters = '%s', filter_names = '%s', filter_cts = '%s', protocol = '%s', magneto_protocol = '%s' where id=%d" % (filters, filterNames, filter_cts, protocol, magnetoProtocol, idx))
	result = cursor.rowcount == 1
	conn.commit()
	conn.close()

	return result

# all raw data using json dumps function.
def saveHistory(testDate, target, filterData, ct, result, graphdata, tempData):
	conn = db.connect('database.db')
	conn.execute("insert into history (testdate, target, filter, ct, result, graphdata, tempdata) values('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (testDate, target, filterData, ct, result, graphdata, tempData))
	conn.commit()
	conn.close()


def getHistoryList():
	conn = db.connect('database.db')
	cursor = conn.execute("select id, testdate, target, filter, ct, result from history")
	data = cursor.fetchall()

	result = []
	for d in data:
		temp = {"id":d[0], "date":d[1], "target":d[2], "filter":d[3], "ct":d[4], "result":d[5]}
		result.append(temp)

	conn.close()
	return result

def getHistoryGraphData(idx):
	conn = db.connect('database.db')
	cursor = conn.execute('select graphdata from history where id=%d' % idx)
	data = cursor.fetchall()

	result = ""

	if len(data) == 1:
		result = data[0][0]

	conn.close()
	return result

def getHistoryTempData(idx):
	conn = db.connect('database.db')
	cursor = conn.execute('select tempdata from history where id=%d' % idx)
	data = cursor.fetchall()

	result = ""

	if len(data) == 1:
		result = data[0][0]

	conn.close()
	return result