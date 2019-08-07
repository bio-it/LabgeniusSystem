# -*- coding: utf-8 -*-

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


import sqlite3 as db

def getRecentProtocol():
	config = ConfigParser()
	config.read('database.ini')

	try:
		protocolIdx = config.getint('data', 'recent_protocol')

		# load protocol from database
	except:
		# Load default protocol
		pass


def setRecentProtocol(protocolIdx):
	config = ConfigParser()
	config.read('database.ini')

	config.set('data', 'recent_protocol', protocolIdx)

	with open('database.ini', 'w') as configFile:
		config.write(configFile)


# Protocol database
def getProtocolList():
	result = []
	conn = db.connect('database.db')
	cursor = conn.execute('select * from protocols')
	data = cursor.fetchall()
	print(data)
	conn.close()
	return result

def insertNewProtocol(name, protocol):
	conn = db.connect('database.db')
	conn.execute("insert into protocols (name, protocol) values('%s', '%s')" % (name, protocol))
	conn.commit()
	conn.close()