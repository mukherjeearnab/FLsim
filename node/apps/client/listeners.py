'''
Module containing listeners to flags
'''
import traceback
from time import sleep
from env import env
from helpers.argsparse import args
from helpers.http import get
from helpers.logging import logger

logicon_url = env['LOGICON_URL']
DELAY = env['DELAY']
node_id = args['node_id']


def wait_for_jobsheet_flag(job_name: str, cluster_id: str):
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

            listen_abort(job_name, cluster_id,
                         abort_flag)

            if prev_flag != jobsheet_flag:
                logger.info(
                    f"Got jobsheet download flag [{jobsheet_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = jobsheet_flag

            # if download jobsheet flag is true, break and exit
            if jobsheet_flag:
                break

        except Exception:
            logger.error(
                f'Failed to fetch jobsheet download flag.\n{traceback.format_exc()}')

        sleep(DELAY)


def wait_for_dataset_flag(job_name: str, cluster_id: str):
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

            listen_abort(job_name, cluster_id,
                         abort_flag)

            if prev_flag != dataset_flag:
                logger.info(
                    f"Got dataset download flag [{dataset_flag}], expecting [True] for [{job_name}] at cluster {cluster_id}")
                prev_flag = dataset_flag

            # if download dataset flag is true, break and exit
            if dataset_flag:
                break

        except Exception:
            logger.error(
                f'Failed to fetch dataset download flag.\n{traceback.format_exc()}')

        sleep(DELAY)


def listen_abort(job_name: str, cluster_id: str, abort_signal: bool):
    '''
    Exit job process if abort signal is received
    '''

    if abort_signal:
        logger.info(
            f'Received Abort Signal. Exiting Job Process for [{job_name}] at cluster [{cluster_id}].')
        update_client_status(node_id, job_id, 5, server_url)
        exit()
