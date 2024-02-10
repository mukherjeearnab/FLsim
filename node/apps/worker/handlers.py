'''
Logic Handlers
'''
import dill
import base64
import traceback
import numpy
from env import env
from base.learn_strategy import LearnStrategyBase
from helpers.argsparse import args
from helpers.logging import logger
from helpers.file import check_OK_file, get_OK_file, create_dir_struct, torch_read
from helpers import p2p_store
from helpers.torch import get_device
from helpers.converters import tensor_to_data_loader
from apps.common.setters import _fail_exit
from apps.common import getters

datadist_url = env['DATADIST_URL']
node_id = args['node_id']


def download_dataset_metadata(job_name: str, cluster_id: str, node_type: str):
    '''
    Download and process the dataset metadata and return the following:

    dataset_path, file_path, timestamp
    '''

    dataset_metadata = getters.get_dataset_metadata(
        job_name, cluster_id, node_type)

    file_path = dataset_metadata['file']
    dataset_path = dataset_metadata['path']
    timestamp = dataset_metadata['timestamp']

    return dataset_path, file_path, timestamp


def download_dataset(job_name: str, cluster_id: str, node_type: str, dataset_path: str, file_path: str, timestamp: str):
    '''
    Checks the version and Donwloads the dataset and returns the file_name and dataset_path

    Returns:
        file_name, dataset_path
    '''
    create_dir_struct(dataset_path)

    is_downloaded = True
    if check_OK_file(dataset_path):
        ok_timestamp = get_OK_file(dataset_path)

        if timestamp != ok_timestamp:
            is_downloaded = False
    else:
        is_downloaded = False

    # download dataset
    if not is_downloaded:
        getters.get_dataset(job_name, cluster_id, node_type,
                            file_path, dataset_path, timestamp)

    file_name = file_path.split('/')[-1]

    return file_name, dataset_path


def load_dataset(job_name: str, cluster_id: str, node_type: str, file_name: str, dataset_path: str):
    '''
    Load the downloaded test dataset on memory
    '''

    try:
        global_test_set = torch_read(file_name, dataset_path)

        return global_test_set
    except Exception:
        logger.error(
            f'Failed to load Global Test Dataset. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def create_data_loaders(test_set, manifest: dict):
    '''
    Create data loaders for training and testing sets

    Returns:
        train_loader, test_loader
    '''

    # if instance of datasets are numpy arrays, not need for data loader
    if isinstance(test_set[0], numpy.ndarray):
        return test_set

    global_test_loader = tensor_to_data_loader(test_set,
                                               manifest['aggregator_params']['batch_size'])

    return global_test_loader


def init_strategy(job_name: str, cluster_id: str, node_type: str, manifest: dict) -> LearnStrategyBase:
    '''
    Initialize the strategy as defined in the job manifest and return the instance
    '''

    try:
        hyperparams = {
            'test_batch_size': manifest['aggregator_params']['batch_size'],
            'worker_extra_params': manifest['aggregator_params']['extra_params']
        }

        dataset_params = manifest['dataset_params']['distribution']

        StrategyClass = dill.loads(base64.b64decode(
            manifest['model_params']['strategy']['definition'].encode()))

        device = get_device() if env['WORKER_USE_CUDA'] == 1 else 'cpu'

        strategy = StrategyClass(
            hyperparams, dataset_params, is_local=False, device=device)

        return strategy
    except Exception:
        logger.error(
            f'Failed to init Strategy. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_client_params(job_name: str, cluster_id: str, node_type: str) -> list:
    '''
    Download the trained client params, load them as state_dict(s) and return
    '''

    client_params = getters.get_client_params(
        job_name, cluster_id, node_type)

    dataset_metadata = getters.get_dataset_metadata(
        job_name, cluster_id, node_type)

    for client_id, payload in client_params.items():
        # fetch the params from the p2p store
        payload['param'] = p2p_store.getv(payload['param'])

        # also add the client's dataset weight
        payload['weight'] = dataset_metadata['weights'][client_id]

    return client_params


def run_aggregator(job_name: str, cluster_id: str, node_type: str,
                   strategy: LearnStrategyBase, client_params: dict):
    '''
    Method to execute the aggregator
    '''
    try:
        for _, client_payload in client_params.items():
            strategy.append_client_object(client_payload['param'],
                                          client_payload['weight'])

        strategy.aggregate()
    except Exception:
        logger.error(
            f'Failed to aggregate params. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def test_model(job_name: str, cluster_id: str, node_type: str,
               strategy: LearnStrategyBase):
    '''
    Test the Aggregated Global Model
    '''
    try:
        metrics = strategy.test()

        return metrics
    except Exception:
        logger.error(
            f'Failed to test model. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_global_state(job_name: str, cluster_id: str, node_type: str):
    '''
    Download and load the global state as LearningStrategy state
    '''

    param_key, _ = getters.get_global_param(
        job_name, cluster_id, node_type)

    param = p2p_store.getv(param_key)

    return param
