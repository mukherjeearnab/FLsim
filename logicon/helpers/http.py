'''
HTTP comms module, with simplified syntax to avoid code repetition
'''
import requests


def get(url: str, params={}, timeout=3600) -> dict:
    '''
    GET request method
    '''
    req = requests.get(url, params, timeout=timeout)
    data = req.json()

    return data


def post(url: str, params: dict, timeout=3600) -> dict:
    '''
    POST request method
    '''
    req = requests.post(url, json=params, timeout=timeout)
    data = req.json()

    return data
