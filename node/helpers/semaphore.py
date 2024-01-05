
'''
Semaphore Wrapper Module
'''
from threading import Semaphore as Original


class Semaphore(Original):
    '''
    Wrapper Class for Semaphores to include a wait function.
    '''
    def wait(self):
        '''
        New Function wait
        '''
        while self._value == 0:
            pass
    