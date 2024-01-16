'''
Module for Global State
'''
from multiprocessing import Manager

manager = Manager()

global_state = manager.dict()

# init peer state
peer_state = manager.dict()
peer_state['node_info'] = dict()
peer_state['peers'] = dict()

# init job process state
jobs_proc_state = dict()
