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


def main():
    while True:
        try:
          recv_data = listener.recv_json()
        except Exception as e:
            logger.error(e)
            continue  
        result, reason, data = magneto_task.run_command(recv_data)
    
        response = { 'result' : result , 'reason' : reason, 'data' : data }
        listener.send_json(response)


if __name__ == '__main__':
    magneto_task.start()
    main()