'''
The Performance Logging Module
'''
import os
from dotenv import load_dotenv
from helpers.http import post
from helpers.logging import logger

load_dotenv()

PERFLOG_URL = os.getenv('PERFLOG_URL')


def init_project(job_name: str, config: dict):
    '''
    Initialize the project at PerfLog Server
    '''
    post(f'{PERFLOG_URL}/init_project',
         {'job_name': job_name, 'config': config})
    logger.info(f'PerfLog initialized for Job [{job_name}]')


def add_record(job_name: str, cluster_id: str, node_id: str, node_type: str,
               round_num: int, epoch_num: int, metrics: dict,  time_delta: float):
    '''
    Add Metrics Record
    '''
    post(f'{PERFLOG_URL}/add_record',
         {'job_name': job_name, 'cluster_id': cluster_id, 'node_id': node_id, 'node_type': node_type,
          'round_num': round_num, 'epoch_num': epoch_num, 'metrics': metrics, 'time_delta': time_delta})
    logger.info(
        f'Adding PerfLog Metrics for Job [{job_name}] at Round {round_num}')


def add_params(job_name: str, round_num: int, params: dict):
    '''
    Save the Global Parameters
    '''
    post(f'{PERFLOG_URL}/add_params',
         {'job_name': job_name, 'round_num': round_num, 'params': params})
    logger.info(
        f'Adding PerfLog Params for Job [{job_name}] at Round {round_num}')


def save_logs(job_name: str):
    '''
    Final Save the Performance Logs
    '''
    post(f'{PERFLOG_URL}/save_logs', {'job_name': job_name})
    logger.info(
        f'Saved PerfLog Metrics for Job [{job_name}]')


def terminate(job_name: str):
    '''
    Terminate the logging process
    '''
    post(f'{PERFLOG_URL}/terminate', {'job_name': job_name})
    logger.info(
        f'Terminating PerfLog Metrics for Job [{job_name}]')
