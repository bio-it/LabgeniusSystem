# -*- coding: utf-8 -*-

import pickle
import logging
import sqlite3 as db
import json

import socket
import subprocess

import os

# test code
import platform

from collections import defaultdict

# logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def getIpAddress():
	if platform.system() == 'Windows':
		return socket.gethostbyname(socket.gethostname())
	else :
		return subprocess.check_output(['hostname', '-I']).decode('ascii').strip()

def getRecentProtocol():
	# default protocol
	# defaultProtocol = [{"label":"1", "temp":95.0, "time":10},{"label":"2", "temp":95.0, "time":5},{"label":"3", "temp":55.0, "time":5},{"label":"4", "temp":72.0, "time":5},{"label":"GOTO", "temp":2.0, "time":10},{"label":"5", "temp":72.0, "time":5}]
	# defaultProtocol = [{"label":"1", "temp":95.0, "time":10},{"label":"2", "temp":95.0, "time":5},{"label":"SHOT", "temp":0.0, "time":0},{"label":"GOTO", "temp":2.0, "time":19},{"label":"5", "temp":72.0, "time":5}]
	# print(defaultProtocol)
	# defaultMagnetoProtocol = ["ready"]
	defaultProtocol = [{"label":"1", "temp":95, "time":10},{"label":"2", "temp":95, "time":5},{"label":"3", "temp":55, "time":5},{"label":"4", "temp":72, "time":5},{"label":"GOTO", "temp":2, "time":4},{"label":"5", "temp":72, "time":5}]
	defaultMagnetoProtocol = ["ready"]

	filters = { 
		'FAM' : { 'use' : False, 'name' : '', 'ct' : 38.0}, 
		'HEX' : { 'use' : False, 'name' : '', 'ct' : 38.0}, 
		'ROX' : { 'use' : False, 'name' : '', 'ct' : 38.0}, 
		'CY5' : { 'use' : False, 'name' : '', 'ct' : 38.0},
	}

	try:
		with open('database.prop', 'rb') as f:
			protocolName = pickle.load(f)	# line by line
			targetFilters = pickle.load(f)
			filterNames = pickle.load(f)
			filterCts = pickle.load(f)
			protocol = pickle.load(f)
			magnetoProtocol = pickle.load(f)

			# save to list data
			protocol = json.loads(protocol)
			magnetoProtocol = json.loads(magnetoProtocol)

			for index in range(len(targetFilters)):
				targetFilter = targetFilters[index]
				filterName = filterNames[index]
				filterCt = filterCts[index]

				filters[targetFilter]['use'] = True
				filters[targetFilter]['name'] = filterName
				filters[targetFilter]['ct'] = filterCt

	except Exception as e:
		logger.info(str(e))
		# Load the first protocol and setting the default protocol
		logger.info("No recent protocol data.")

		protocolList = getProtocolList()
		print(protocolList)
		# No protocol list on the database, make new protocol
		if len(protocolList) == 0:
			protocolName = 'Default protocol'
			targetFilters = ['FAM']
			filterNames = ['CT']
			filterCts = ['38.0']
			protocol = defaultProtocol
			magnetoProtocol = defaultMagnetoProtocol

		else: # Load the first protocol.
			# protocolName = protocolList[0][1]
			# targetFilters = protocolList[0][2].strip().split(',')
			# filterNames = protocolList[0][3].strip().split(',')
			# filterCts = protocolList[0][4].strip().split(',')
			# protocol = protocolList[0][5]
			# magnetoProtocol = protocolList[0][6]
			protocolName = protocolList[0]['name']
			targetFilters = protocolList[0]['filters'].strip().split(', ')
			filterNames = protocolList[0]['filterNames'].strip().split(', ')
			filterCts = protocolList[0]['filterCts'].strip().split(', ')
			protocol = protocolList[0]['protocol']
			magnetoProtocol = protocolList[0]['magnetoProtocol']

			# save to list data
			protocol = json.loads(protocol)
			magnetoProtocol = json.loads(magnetoProtocol)

		
		setRecentProtocol(protocolName, targetFilters, filterNames, filterCts, json.dumps(protocol), json.dumps(magnetoProtocol))
		# setRecentProtocol(protocolName, filters, filterNames, filterCts, json.dumps(protocol), json.dumps(magnetoProtocol))
		# setRecentProtocol(protocolName, filters, json.dumps(protocol), json.dumps(magnetoProtocol))
	for index in range(len(targetFilters)):
		targetFilter = targetFilters[index]
		filterName = filterNames[index]
		filterCt = filterCts[index]

		filters[targetFilter]['use'] = True
		filters[targetFilter]['name'] = filterName
		filters[targetFilter]['ct'] = filterCt

	# return (protocolName, filters, filterNames, filterCts, protocol, magnetoProtocol)
	return (protocolName, filters, protocol, magnetoProtocol)

def setRecentProtocol(name, filters, filterNames, filterCts, protocol, magnetoProtocol):
	# protocolData = { 'filters' : [], 'protocol' : [], 'magnetoProtocol' : []}
	# for i, val in enumerate(['FAM', 'HEX', 'ROX', 'CY5']):
	# 	protocolData['filters'].append({ val : })
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

# create database tables (history, protocols (optional) version)
def createDatabaseTables():
	conn = db.connect('database.db')
	# conn.execute('''
	# 				create table if not exists protocols(
	# 					id integer not null primary key autoincrement,
	# 					name text not null,
	# 					filters text not null,
	# 					protocol text not null, 
	# 					magneto_protocol text not null default(''),
	# 					created_date datetime default (datetime('now', 'localtime'))
	# 				)
	# 			 ''')
	conn.execute('''
					create table if not exists protocols(
						id integer not null primary key autoincrement,
						name text not null,
						filters text not null,
						created_date datetime default (datetime('now', 'localtime')),
						protocol text not null, 
						filter_names text not null default(''), 
						filter_cts text not null default(''), 
						magneto_protocol text not null default('')
					)
				 ''')
	
	# create history table
	conn.execute('''
					create table if not exists history(
						id integer not null primary key autoincrement,
						testdate datetime default (datetime('now', 'localtime')),
						target text not null,
						filter text not null,
						ct text not null,
						result text not null,
						graphdata text not null, 
						tempData text not null default('')
					)
				''')
	# create version table
	# conn.execute('create table if not exists version (id integer not null primary key autoincrement, _datetime datetime default(datetime("now", "localtime")))')
	
	# create constant table
	conn.execute('''
					create table if not exists constant(
						id integer not null primary key autoincrement,
						maxCycle integer not null,
						compensation integer not null,
						integralMax real not null,
						displayDelta real not null,
						flRelativeMax real not null,
						pids text not null
					)
				''')
	
	conn.commit()
	conn.close()

# Protocol database
def getProtocolList():
	conn = db.connect('database.db')
	cursor = conn.execute('select id, name, filters, filter_names, filter_cts, protocol, magneto_protocol from protocols')
	# cursor = conn.execute('select id, name, filters, protocol, magneto_protocol from protocols')
	data = cursor.fetchall()

	result = []
	for d in data:
		temp = {"id":d[0], "name":d[1], "filters":d[2], "filterNames":d[3], "filterCts":d[4], "protocol":d[5], "magnetoProtocol":d[6]}
		# temp = {"id":d[0], "name":d[1], "filters":d[2], "protocol":d[3], "magnetoProtocol":d[4]}
		result.append(temp)

	conn.close()
	return result

def insertProtocol(name, filters, filterNames, filterCts, protocol, magnetoProtocol):
	conn = db.connect('database.db')
	# conn.execute("insert into protocols (name, filters, protocol, magneto_protocol) values('%s', '%s', '%s', '%s')" % (name, filters, protocol, magnetoProtocol))
	conn.execute("insert into protocols (name, filters, filter_names, filter_cts, protocol, magneto_protocol) values('%s', '%s', '%s', '%s', '%s', '%s')" % (name, filters, filterNames, filterCts, protocol, magnetoProtocol))
	conn.commit()
	conn.close()

def checkProtocolExist(name):
	conn = db.connect('database.db')
	cursor = conn.execute("select name from protocols where name='%s'" % name)
	data = cursor.fetchall()
	conn.close()

	if len(data) != 0:
		return True
	else:
		return False

def getProtocol(idx):
	conn = db.connect('database.db')
	# cursor = conn.execute('select name, filters, protocol, magneto_protocol from protocols where id="%d"' % idx)
	cursor = conn.execute('select name, filters, filter_names, filter_cts, protocol, magneto_protocol from protocols where id="%d"' % idx)
	data = cursor.fetchall()

	result = {}

	if len(data) == 1:
		data = data[0]
		filters = {}
		# result = {"name":data[0][0], "filters":data[0][1], "filterNames":data[0][2], "filterCts":data[0][3], "protocol":data[0][4], "magnetoProtocol":data[0][5]}
		result = {"name":data[0], "filters":data[1], "filterNames":data[2], "filterCts":data[3], "protocol":data[4], "magnetoProtocol":data[5]}
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
	# cursor = conn.execute("update protocols set filters = '%s', protocol = '%s', magneto_protocol = '%s' where id=%d" % (filters, protocol, magnetoProtocol, idx))
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
		print(temp)
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

def updateConstants():
	pass

def loadConstants():
	pids = defaultdict(lambda : {"startTemp" : 0.0, "tartgetTemp" : 0.0, "kp" : 0.0, "ki" : 0.0, "kd" : 0.0}) 
	# TODO : load constants (maxCycles, compensation, integralMax, displayDelta, flRelativeMax, pids)
	# if len(pids) == 0:
	conn = db.connect('database.db')


		

