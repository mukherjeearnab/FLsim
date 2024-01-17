'''
Getters for Job
'''
import traceback
from typing import Tuple
from env import env
from helpers.argsparse import args
from helpers.http import get, download_file
from helpers.file import set_OK_file
from helpers.logging import logger
from apps.common.setters import _fail_exit

logicon_url = env['LOGICON_URL']
datadist_url = env['DATADIST_URL']
DELAY = env['DELAY']
node_id = args['node_id']


def get_dataset_metadata(job_name: str, cluster_id: str, node_type: str) -> dict:
    '''
    Fetch the Dataset Metadata from Dataset Distributor
    '''

    url = f'{datadist_url}/get_dataset_metadata'
    client_id = node_id if node_type == 'client' else 'global_test'

    try:
        manifest = get(
            url, {'job_name': job_name, 'cluster_id': cluster_id, 'client_id': client_id})

        logger.info(
            f'[{node_type}] Downloaded dataset metadata for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}]')

        return manifest
    except Exception:
        logger.error(
            f'[{node_type}] Failed to download dataset metadata for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}].\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_dataset(job_name: str, cluster_id: str, node_type: str, file_path: str, dataset_path: str, timestamp: str) -> None:
    '''
    Fetch the Dataset from Dataset Distributor
    '''

    client_id = node_id if node_type == 'client' else 'global_test'
    url = f'{datadist_url}/download_dataset?job_name={job_name}&cluster_id={cluster_id}&client_id={client_id}'

    try:
        download_file(url,
                      file_path)
        set_OK_file(dataset_path, timestamp)

        logger.info(
            f'[{node_type}] Downloaded dataset for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}]')

    except Exception:
        logger.error(
            f'[{node_type}] Failed to download dataset for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}].\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_job_config(job_name: str, cluster_id: str, node_type: str) -> dict:
    '''
    Get Job Config for a given job at a given cluster for a given node
    node_type: str = [client, worker]
    '''

    url = f'{logicon_url}/job/get_config'

    try:
        manifest = get(
            url, {'job_name': job_name, 'cluster_id': cluster_id, 'config_type': node_type})['payload']
        node_config = manifest[node_id]

        logger.info(
            f'[{node_type}] Downloaded job config for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}]')

        return node_config
    except Exception:
        logger.error(
            f'[{node_type}] Failed to download job config for [{job_name}] at [{cluster_id}] for {node_type} [{node_id}].\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_global_param(job_name: str, cluster_id: str, node_type: str) -> Tuple[str, str]:
    '''
    Get Global Params for a given job at a given cluster

    Returns:
        param_key, extra_data_key
    '''

    url = f'{logicon_url}/job/get_exec_params'

    try:
        manifest = get(
            url, {'job_name': job_name, 'cluster_id': cluster_id})['payload']

        param_key = manifest['global_model_param']['param']
        extra_data_key = manifest['global_model_param']['extra_data']

        logger.info(
            f'[{node_type}] Downloaded global param for [{job_name}] at [{cluster_id}]')

        return param_key, extra_data_key
    except Exception:
        logger.error(
            f'[{node_type}] Failed to download global param for [{job_name}] at [{cluster_id}].\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_client_params(job_name: str, cluster_id: str, node_type: str) -> dict:
    '''
    Get Client Params for a given job at a given cluster

    Returns:
        param_key, extra_data_key
    '''

    url = f'{logicon_url}/job/get_exec_params'

    try:
        manifest = get(
            url, {'job_name': job_name, 'cluster_id': cluster_id})['payload']

        client_params = manifest['client_trained_params']

        logger.info(
            f'[{node_type}] Downloaded client params for [{job_name}] at [{cluster_id}]')

        return client_params
    except Exception:
        logger.error(
            f'[{node_type}] Failed to download client params for [{job_name}] at [{cluster_id}].\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)
