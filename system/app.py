# main_server.py
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cors import CORS
from api.task_worker import TaskWorker
from api import api as bp
from api import util

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':\
    # create database tables, if it doesn't exist
    util.createDatabaseTables()

    # Initialize the task worker thread and start
    task_worker = TaskWorker.instance()
    task_worker.start()

    # Initialize the flask server
    app = Flask(__name__)
    cors = CORS(app, resources={
        r"/api/*": {"origins": "*"}
        })
        
    # PCR API 
    app.register_blueprint(bp.bp_task, url_prefix='/api/task')
    app.register_blueprint(bp.bp_protocol, url_prefix='/api/protocol')
    app.register_blueprint(bp.bp_history, url_prefix='/api/history')
    app.register_blueprint(bp.bp_magneto, url_prefix='/api/magneto')

    # Magneto API
    # app.run(host=util.getIpAddress(), port=6009, debug=True, use_reloader=False)
    app.run(host='0.0.0.0', port=6009, debug=True, use_reloader=False)
