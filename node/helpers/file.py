'''
YAML file management module
'''
import time
from typing import Any
from os.path import exists
from os import makedirs
import yaml
import torch
from helpers.logging import logger


def file_exists(filename: str) -> bool:
    '''
    Function to check if a file exists or not
    '''

    return exists(filename)


def read_yaml_file(filename: str) -> dict:
    '''
    Function to read a YAML file from Disk and return a dictionary.
    '''

    with open(filename, 'r', encoding='utf8') as file:
        yaml_dict = yaml.safe_load(file)

    return yaml_dict


def read_py_module(filename: str) -> str:
    '''
    Function to read a python module from disk and return it as string.
    '''

    with open(f'{filename}.py', 'r', encoding='utf8') as file:
        module = file.read()

    return module


def torch_write(filename: str, path: str, contents: Any):
    '''
    Function to save a torch tensor or a tuple of torch tensors to disk.
    '''
    torch.save(contents, f'{path}/{filename}')
    logger.info(f'Saved file [{filename}] to disk using torch.save')


def torch_read(filename: str, path: str):
    '''
    Function to read a torch tensor or a tuple of torch tensors from disk.
    '''
    contents = torch.load(f'{path}/{filename}')
    logger.info(f'Loaded file [{filename}] from disk using torch.load')

    return contents


def set_OK_file(path: str, timestamp=None):
    '''
    Sets a Flag file named OK
    '''
    ok_time = int(time.time()) if timestamp is None else timestamp

    with open(f'{path}/OK', 'w', encoding='utf8') as f:
        f.write(f'{ok_time}')


def check_OK_file(path: str) -> bool:
    '''
    Checks if OK flag file is present in directory.
    '''
    return exists(f'{path}/OK')


def get_OK_file(path: str) -> bool:
    '''
    Reads the OK file if OK flag file is present in directory.
    '''
    if exists(f'{path}/OK'):
        with open(f'{path}/OK', 'r', encoding='utf8') as f:
            read_timestamp = f.read()
    return read_timestamp


def create_dir_struct(path: str) -> None:
    '''
    Creates a directory structure, if it does not exist
    '''

    if not exists(path):
        makedirs(path)
