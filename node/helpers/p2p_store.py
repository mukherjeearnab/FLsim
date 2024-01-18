'''
Key Value Store Module
'''
import json
import traceback
from typing import Any
from time import sleep
from env import env
from helpers import http
from helpers.logging import logger


DELAY = env['DELAY']
KVS_URL = env['P2PSTORE_URL']

#########################
# Wrapper KVStore API
#########################


def getv(key: str) -> Any:
    '''
    Get Value from Key
    '''
    print('P2P GET:', key)

    value = kv_get_legacy(key)

    return value


def setv(value: Any) -> str:
    '''
    Set Value and get Key
    '''
    key = kv_set_legacy(value)

    print('P2P SET:', key)

    return key


def delete(key: str) -> Any:
    '''
    Delete Value with Key
    '''
    print('P2P DEL:', key)

    value = kv_delete_legacy(key)

    return value


###############################
# HTTP-based Legacy KVStore API
###############################

def kv_get_legacy(key: str) -> Any:
    '''
    Get Value from Key
    '''

    try:
        reply = http.get(f'{KVS_URL}/get',
                         {'key': key})
    except Exception:
        logger.error(
            f'KVStore Database Connection Error! Retrying in 30s.\n{traceback.format_exc()}')
        sleep(DELAY*60)

    if reply['status'] == 404:
        return None

    return json.loads(reply['value'])


def kv_set_legacy(value: Any) -> str:
    '''
    Set Value with Key
    '''
    try:
        reply = http.post(f'{KVS_URL}/set', {'value': json.dumps(value)})

    except Exception:
        logger.error(
            f'KVStore Database Connection Error! Retrying in 30s.\n{traceback.format_exc()}')
        sleep(DELAY*60)

    if reply['status'] == 500:
        return None

    return reply['key']


def kv_delete_legacy(key: str) -> Any:
    '''
    Delete Value with Key
    '''
    while True:
        try:
            reply = http.get(f'{KVS_URL}/delete', {'key': key})
            break
        except Exception:
            logger.error(
                f'KVStore Database Connection Error! Retrying in 30s.\n{traceback.format_exc()}')
            sleep(DELAY*6)

    if reply['res'] == 404:
        return None

    return json.loads(reply['value'])
