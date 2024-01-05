'''
Module for Global State
'''
from multiprocessing import Manager

manager = Manager()

global_state = manager.dict()
