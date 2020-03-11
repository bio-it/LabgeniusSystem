# main_server.py
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cors import CORS
from api import api as bp

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Initialize the flask server
    app = Flask(__name__)
    cors = CORS(app, resources={
        r"/api/*": {"origins": "*"}
        })
    app.register_blueprint(bp.bp_pcr, url_prefix='/api/pcr')
    app.register_blueprint(bp.bp_pcr_protocol, url_prefix='/api/pcr/protocol')
    app.register_blueprint(bp.bp_history, url_prefix='/api/history')
    app.run(host='210.115.227.78', port=6009, debug=True, use_reloader=False)
