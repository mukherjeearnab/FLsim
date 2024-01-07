'''
Key Value Store Class
'''
import threading
from hashlib import md5
from typing import Tuple, Union


class KeyValueStore:
    '''
    Key Val Store Class
    '''

    def __init__(self):
        self.table = dict()
        self.locks = dict()

    def get(self, key: str) -> Tuple[Union[str, None], bool]:
        '''
        Get Value
        '''
        if key in self.table:
            return self.table[key], True
        else:
            return None, False

    def set(self, value: str) -> str:
        '''
        Set Value
        '''
        key = hash_function(value)
        if key not in self.locks:
            self.locks[key] = threading.Lock()

        self.locks[key].acquire()

        self.table[key] = value

        self.locks[key].release()

        return key

    def delete(self, key: str) -> Tuple[Union[str, None], bool]:
        '''
        Delete Value
        '''
        if key not in self.locks:
            return None, False
        else:
            self.locks[key].acquire()

            value = self.table[key]

            del self.table[key]

            self.locks[key].release()

            del self.locks[key]

            return value, True

    def check(self, key: str) -> bool:
        '''
        Check if Key has been Set
        '''
        if key in self.table:
            return True
        else:
            return False


def hash_function(value: str) -> str:
    '''
    Return the MD5 hash of a string value
    '''
    return md5(value.encode()).hexdigest()
