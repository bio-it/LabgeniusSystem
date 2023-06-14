import os
import zmq
import logging
import threading 
from magneto.magneto_task import MagnetoTask


logger = logging.getLogger(__name__)

MAGNETO_PORT = os.environ.get('MAGNETO_PORT', '7005')

context = zmq.Context()
listener = context.socket(zmq.REP)
listener.bind('tcp://*:%s' % MAGNETO_PORT)
magneto_task = MagnetoTask()
magneto_task.start()


while True:
    try:
        command = listener.recv_string()
    except Exception as e:
        logger.error(e)
        continue  

    if len(command) == 0:
        command = 'get_status'

    print(command)
    result, reason, data = magneto_task.run_command(command)

    listener.send_json({ 'result' : result , 'reason' : reason, 'data' : data })

