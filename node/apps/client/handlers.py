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
from helpers.file import check_OK_file, get_OK_file, create_dir_struct
from helpers import p2p_store
from helpers.torch import get_device
from helpers.converters import tensor_to_data_loader
from apps.client import training
from apps.common.setters import _fail_exit
from apps.common import getters

datadist_url = env['DATADIST_URL']
node_id = args['node_id']


def init_strategy(job_name: str, cluster_id: str, node_type: str, manifest: dict) -> LearnStrategyBase:
    '''
    Initialize the strategy as defined in the job manifest and return the instance
    '''

    try:
        hyperparams = {
            'train_batch_size': manifest['train_params']['batch_size'],
            'test_batch_size': manifest['train_params']['batch_size'],
            'learning_rate': manifest['train_params']['learning_rate'],
            'train_epochs': manifest['train_params']['local_epochs'],
            'client_extra_params': manifest['train_params']['extra_params']
        }

        dataset_params = manifest['dataset_params']['distribution']

        StrategyClass = dill.loads(base64.b64decode(
            manifest['model_params']['strategy']['definition'].encode()))

        device = get_device() if env['CLIENT_USE_CUDA'] == 1 else 'cpu'

        strategy = StrategyClass(
            hyperparams, dataset_params, is_local=True, device=device)

        return strategy
    except Exception:
        logger.error(
            f'Failed to init Model. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def load_dataset(job_name: str, cluster_id: str, node_type: str, file_name: str, dataset_path: str, strategy: LearnStrategyBase):
    '''
    Load the downloaded dataset on memory and execute the preprocessing scripts on it.
    '''

    try:
        (train_set, test_set) = training.data_preprocessing(file_name, dataset_path,
                                                            strategy)

        return train_set, test_set
    except Exception:
        logger.error(
            f'Failed to run Dataset Proprocessing. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def parameter_mixing(job_name: str, cluster_id: str, manifest: dict, node_type: str, global_model, prev_local_model):
    '''
    Use the Parameter Mixing algorithm to mix the global and prev local model parameters to create the current model params
    '''

    try:
        curr_params = training.parameter_mixing(global_model.state_dict(), prev_local_model.state_dict(),
                                                manifest['model_params']['parameter_mixer']['content'])
        return curr_params
    except Exception:
        logger.error(
            f'Failed to mix parameters. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def train_model(job_name: str, cluster_id: str, node_type: str,
                strategy: LearnStrategyBase):
    '''
    Train the Local Model
    '''
    try:
        logger.info(
            f'Starting Local Training with {strategy.train_epochs} EPOCHS')
        strategy.train()
        logger.info(
            f'Completed Local Training with {strategy.train_epochs} EPOCHS')
    except Exception:
        logger.error(
            f'Failed to train model. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def test_model(job_name: str, cluster_id: str, node_type: str,
               strategy: LearnStrategyBase):
    '''
    Test the Local Model
    '''
    try:
        metrics = strategy.test()

        return metrics
    except Exception:
        logger.error(
            f'Failed to test Strategy. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def create_data_loaders(train_set, test_set, manifest: dict):
    '''
    Create data loaders for training and testing sets

    Returns:
        train_loader, test_loader
    '''

    # if instance of datasets are numpy arrays, not need for data loader
    if isinstance(train_set[0], numpy.ndarray) and isinstance(test_set[0], numpy.ndarray):
        return train_set, test_set

    train_loader = tensor_to_data_loader(train_set,
                                         manifest['train_params']['batch_size'])
    test_loader = tensor_to_data_loader(test_set,
                                        manifest['train_params']['batch_size'])

    return train_loader, test_loader


def get_global_state(job_name: str, cluster_id: str, node_type: str) -> str:
    '''
    Download and load the global state as LearningStrategy state
    '''

    param_key, _ = getters.get_global_param(
        job_name, cluster_id, node_type)

    global_state = p2p_store.getv(param_key)

    return global_state


def download_dataset_metadata(job_name: str, cluster_id: str, node_type: str):
    '''
    Download and process the dataset metadata and return the following:

    dataset_path, file_path, timestamp
    '''

    dataset_metadata = getters.get_dataset_metadata(
        job_name, cluster_id, node_type)
    file_path = dataset_metadata['file']
    dataset_path = file_path.replace('/index.tuple', '')
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
