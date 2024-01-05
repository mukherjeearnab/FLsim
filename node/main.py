'''
This is the Commandline interface for managing the server
'''
import sys
import logging
from time import sleep
from state import global_state
# from helpers.argsparse import args
# from helpers.logging import logger
# from helpers import torch as _
from apps.servers import controller, gossip

# set flask logging level
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

global_state['testv'] = 'adsf'

# start the servers
controller.start_server()
gossip.start_server()
sleep(1)

if __name__ == '__main__':
    while True:
        testv = input("Enter TESTV: ")
        global_state['testv'] = testv
