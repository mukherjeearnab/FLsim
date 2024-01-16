'''
Module containing listeners to flags
'''
import traceback
from time import sleep
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

    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id})

            jobsheet_flag = manifest['job_status']['download_jobsheet']
            abort_flag = manifest['job_status']['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != jobsheet_flag:
                logger.info(
                    f"Got jobsheet download flag [{jobsheet_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = jobsheet_flag

            # if download jobsheet flag is true, break and exit
            if jobsheet_flag:
                break

        except Exception:
            logger.error(
                f'Failed to fetch jobsheet download flag. Aborting.\n{traceback.format_exc()}')
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY)


def wait_for_dataset_flag(job_name: str, cluster_id: str, node_type: str):
    '''
    Method to wait for dataset download flag
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id})

            dataset_flag = manifest['job_status']['download_dataset']
            abort_flag = manifest['job_status']['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != dataset_flag:
                logger.info(
                    f"Got dataset download flag [{dataset_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = dataset_flag

            # if download dataset flag is true, break and exit
            if dataset_flag:
                break

        except Exception:
            logger.error(
                f'Failed to fetch dataset download flag. Aborting.\n{traceback.format_exc()}')
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY)


def wait_for_start_end_training(job_name: str, cluster_id: str, node_type: str) -> int:
    '''
    Method to wait for process_stage to turn 1 or 3
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id})

            process_stage = manifest['job_status']['process_stage']
            abort_flag = manifest['job_status']['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != process_stage:
                logger.info(
                    f"Got process_stage [{process_stage}], expecting [1,3] for [{job_name}] at cluster {cluster_id}")
                prev_flag = process_stage

            # if process_stage is 1, break and exit
            if process_stage == 1 or process_stage == 3:
                break

            return process_stage
        except Exception:
            logger.error(
                f'Failed to fetch process_stage flag. Aborting.\n{traceback.format_exc()}')
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY)


def wait_for_aggregation_phase(job_name: str, cluster_id: str, node_type: str) -> int:
    '''
    Method to wait for process_stage to turn 2
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id})

            process_stage = manifest['job_status']['process_stage']
            abort_flag = manifest['job_status']['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != process_stage:
                logger.info(
                    f"Got process_stage [{process_stage}], expecting [2] for [{job_name}] at cluster {cluster_id}")
                prev_flag = process_stage

            # if process_stage is 1, break and exit
            if process_stage == 2:
                break

            return process_stage
        except Exception:
            logger.error(
                f'Failed to fetch process_stage flag. Aborting.\n{traceback.format_exc()}')
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY)


def wait_for_node_stage(job_name: str, cluster_id: str, node_type: str, stage: int):
    '''
    Method to wait for process_stage to turn 1
    '''
    prev_flag = -1
    # listen to check if dataset flag is true or false
    url = f'{logicon_url}/job/get_job_status'

    while True:
        try:

            manifest = get(url, {'job_name': job_name,
                           'cluster_id': cluster_id})

            node_stage = manifest['job_status'][f'{node_type}_stage']
            abort_flag = manifest['job_status']['abort']

            listen_abort(job_name, cluster_id, node_type, abort_flag)

            if prev_flag != node_stage:
                logger.info(
                    f"Got {node_type}_stage [{node_stage}], expecting [{stage}] for [{job_name}] at cluster {cluster_id}")
                prev_flag = node_stage

            # if if node_stage matches stage, break and exit
            if node_stage == stage:
                break

        except Exception:
            logger.error(
                f'Failed to fetch {node_type}_stage flag. Aborting.\n{traceback.format_exc()}')
            _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY)


def listen_abort(job_name: str, cluster_id: str, node_type: str, abort_flag: bool):
    '''
    Exit job process if abort signal is received
    '''

    if abort_flag:
        logger.info(
            f'Received Abort Signal. Exiting Job Process for [{job_name}] at cluster [{cluster_id}].')
        _fail_exit(job_name, cluster_id, node_type)
