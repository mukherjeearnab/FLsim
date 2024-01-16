'''
Logic Handlers
'''
import traceback
from env import env
from helpers.argsparse import args
from helpers.logging import logger
from helpers.dynamod import load_module
from helpers.file import check_OK_file, get_OK_file, create_dir_struct, torch_read
from helpers import p2p_store
from helpers.torch import get_device
from helpers.converters import tensor_to_data_loader, convert_base64_to_state_dict
from apps.worker import aggregation
from apps.common.setters import _fail_exit
from apps.common import getters
from apps.client import training

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

    global_test_loader = tensor_to_data_loader(test_set,
                                               manifest['aggregator_params']['batch_size'])

    return global_test_loader


def init_model(job_name: str, cluster_id: str, manifest: dict, node_type: str):
    '''
    Initialize the model as defined in the job manifest and return the instance
    '''

    try:
        local_model = training.init_model(
            manifest['model_params']['model_file']['content'])
        return local_model
    except Exception:
        logger.error(
            f'Failed to init Model. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_client_params(job_name: str, cluster_id: str, node_type: str) -> list:
    '''
    Download the trained client params, load them as state_dict(s) and return
    '''
    device = get_device()

    client_params = getters.get_client_params(
        job_name, cluster_id, node_type)

    dataset_metadata = getters.get_dataset_metadata(
        job_name, cluster_id, node_type)

    for client_id, payload in client_params.items():
        # fetch the params from the p2p store
        payload['param'] = p2p_store.getv(payload['param'])
        # convert to tensor state dict
        payload['param'] = convert_base64_to_state_dict(
            payload['param'], device)

        # fetch the extra_data from the p2p store
        payload['extra_data'] = p2p_store.getv(payload['extra_data_key'])

        # also add the client's dataset weight
        payload['weight'] = dataset_metadata['weights'][client_id]

    return client_params


def run_aggregator(job_name: str, cluster_id: str, node_type: str, manifest: dict,
                   global_model, client_params: dict, extra_data: dict):
    '''
    Method to execute the aggregator
    '''

    global_model = aggregation.aggregate_client_params(job_name, cluster_id, node_type, manifest,
                                                       global_model, client_params, extra_data)

    return global_model


def test_model(job_name: str, cluster_id: str, manifest: dict, node_type: str,
               local_model, test_loader):
    '''
    Test the Aggregated Global Model
    '''
    device = get_device()

    try:
        testing_module = load_module(
            'testing_module', manifest['model_params']['test_file']['content'])
        metrics = testing_module.test_runner(
            local_model, test_loader, device)

        return metrics
    except Exception:
        logger.error(
            f'Failed to test model. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def get_global_param(job_name: str, cluster_id: str, node_type: str):
    '''
    Download and load the global params as pytorch object
    '''

    param_key, extra_data_key = getters.get_global_param(
        job_name, cluster_id, node_type)

    param = p2p_store.getv(param_key)

    if extra_data_key == 'empty':
        extra_data = {}
    else:
        extra_data = p2p_store.getv(extra_data_key)

    return param, extra_data
