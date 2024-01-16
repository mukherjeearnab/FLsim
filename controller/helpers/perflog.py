'''
The Performance Logging Module
'''
import os
from dotenv import load_dotenv
from helpers.http import post
from helpers.logging import logger

load_dotenv()

PERFLOG_URL = os.getenv('PERFLOG_URL')


def init_project(job_id: str, config: dict):
    '''
    Initialize the project at PerfLog Server
    '''
    post(f'{PERFLOG_URL}/init_project', {'job_id': job_id, 'config': config})
    logger.info('PerfLog initialized for Job [{job_id}]')


def add_record(client_id: str, job_id: str, metrics: dict, round_num: int, time_delta: float):
    '''
    Add Metrics Record
    '''
    post(f'{PERFLOG_URL}/add_record',
         {'client_id': client_id, 'job_id': job_id, 'metrics': metrics, 'round_num': round_num, 'time_delta': time_delta})
    logger.info(
        'Adding PerfLog Metrics for Job [{job_id}] at Round {round_num}')


def add_params(job_id: str, round_num: int, params: dict):
    '''
    Save the Global Parameters
    '''
    post(f'{PERFLOG_URL}/add_params',
         {'job_id': job_id, 'round_num': round_num, 'params': params})
    logger.info(
        'Adding PerfLog Params for Job [{job_id}] at Round {round_num}')


def save_logs(job_id: str):
    '''
    Final Save the Performance Logs
    '''
    post(f'{PERFLOG_URL}/save_logs', {'job_id': job_id})
    logger.info(
        'Saved PerfLog Metrics for Job [{job_id}]')
