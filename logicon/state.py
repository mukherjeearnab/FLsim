'''
Module for Global State
'''
from multiprocessing import Manager

manager = Manager()

global_state = manager.dict()

# init job state
job_state = manager.dict()

# job route state
job_route_state = dict()
