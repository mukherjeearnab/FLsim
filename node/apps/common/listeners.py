'''
Module containing listeners to flags
'''
import traceback
from time import sleep
from typing import Tuple
from env import env
from helpers.argsparse import args
from helpers.http import get
from helpers.logging import logger
from apps.common.setters import _fail_exit

logicon_url = env['LOGICON_URL']
DELAY = env['DELAY']
node_id = args['node_id']


def wait_for_jobsheet_flag(job_name: str, cluster_id: str, node_type: str):
    '''
    Method to wait for jobsheet download flag
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id}, timeout=15)['payload']

            jobsheet_flag = manifest['download_jobsheet']
            abort_flag = manifest['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != jobsheet_flag:
                logger.info(
                    f"[{node_type}] Got jobsheet download flag [{jobsheet_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = jobsheet_flag

            # if download jobsheet flag is true, break and exit
            if jobsheet_flag:
                break

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch jobsheet download flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def wait_for_dataset_flag(job_name: str, cluster_id: str, node_type: str):
    '''
    Method to wait for dataset download flag
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id}, timeout=15)['payload']

            dataset_flag = manifest['download_dataset']
            abort_flag = manifest['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != dataset_flag:
                logger.info(
                    f"[{node_type}] Got dataset download flag [{dataset_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = dataset_flag

            # if download dataset flag is true, break and exit
            if dataset_flag:
                break

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch dataset download flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def wait_for_start_end_training(job_name: str, cluster_id: str, node_type: str) -> Tuple[int, int, int]:
    '''
    Method to wait for process_stage to turn 1 or 3
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                                 'cluster_id': cluster_id}, timeout=15)['payload']

            process_stage = manifest['process_stage']
            abort_flag = manifest['abort']
            global_round = manifest['global_round']
            cluster_epoch = manifest['current_epoch']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != process_stage:
                logger.info(
                    f"[{node_type}] Got process_stage [{process_stage}], expecting [1,3] for [{job_name}] at cluster {cluster_id}")
                prev_flag = process_stage

            # if process_stage is 1, break and exit
            if process_stage == 1 or process_stage == 3:
                return process_stage, global_round, cluster_epoch

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch process_stage flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def wait_for_aggregation_phase(job_name: str, cluster_id: str, node_type: str) -> int:
    '''
    Method to wait for process_stage to turn 2
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                                 'cluster_id': cluster_id}, timeout=15)['payload']

            process_stage = manifest['process_stage']
            abort_flag = manifest['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != process_stage:
                logger.info(
                    f"[{node_type}] Got process_stage [{process_stage}], expecting [2] for [{job_name}] at cluster {cluster_id}")
                prev_flag = process_stage

            # if process_stage is 1, break and exit
            if process_stage == 2:
                return process_stage

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch process_stage flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def wait_for_scheduled_execution(job_name: str, cluster_id: str, node_type: str) -> Tuple[int, int, int]:
    '''
    Method to wait for execution signal to be true
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                                 'cluster_id': cluster_id,
                                 'node_id': node_id,
                                 'node_type': node_type}, timeout=15)['payload']

            start_scheduled_execution = manifest['start_scheduled_execution']
            abort_flag = manifest['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != start_scheduled_execution:
                logger.info(
                    f"[{node_type}] Got start_scheduled_execution [{start_scheduled_execution}], expecting True for [{job_name}] at cluster {cluster_id}")
                prev_flag = start_scheduled_execution

            # if process_stage is 1, break and exit
            if start_scheduled_execution:
                return

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch process_stage flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def wait_for_node_stage(job_name: str, cluster_id: str, node_type: str, stage: int):
    '''
    Method to wait for node_stage to turn 1
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    try_count = 0
    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id}, timeout=15)['payload']

            node_stage = manifest[f'{node_type}_stage']
            abort_flag = manifest['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != node_stage:
                logger.info(
                    f"[{node_type}] Got {node_type}_stage [{node_stage}], expecting [{stage}] for [{job_name}] at cluster {cluster_id}")
                prev_flag = node_stage

            # if if node_stage matches stage, break and exit
            if node_stage == stage:
                break

        except Exception:
            logger.error(
                f'[{node_type}] Failed to fetch {node_type}_stage flag. Aborting.\n{traceback.format_exc()}')
            try_count += 1

        if try_count >= 10:
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*5)


def listen_abort(job_name: str, cluster_id: str, node_type: str, abort_flag: bool):
    '''
    Exit job process if abort signal is received
    '''

    if abort_flag:
        logger.info(
            f'[{node_type}] Received Abort Signal. Exiting Job Process for [{job_name}] at cluster [{cluster_id}].')
        _fail_exit(job_name, cluster_id, node_type)
