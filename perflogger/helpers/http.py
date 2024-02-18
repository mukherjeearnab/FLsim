'''
HTTP comms module, with simplified syntax to avoid code repetition
'''
import requests
from urllib.request import urlretrieve


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


def download_file(url: str, filename: str):
    '''
    Method to download a file
    '''
    urlretrieve(url, filename, __show_progress)
    print('\n')


def __show_progress(block_num, block_size, total_size):
    print(
        f'Downloading File: {int(100*(block_num*block_size)/total_size)}%', end='\r')
