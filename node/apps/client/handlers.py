'''
Logic Handlers
'''
import traceback
from env import env
from helpers.argsparse import args
from helpers.logging import logger
from helpers.file import check_OK_file, get_OK_file, create_dir_struct

from apps.client import training
from apps.common import _fail_exit, getters

datadist_url = env['DATADIST_URL']
node_id = args['node_id']


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


def load_dataset(job_name: str, cluster_id: str, node_type: str, file_name: str, dataset_path: str, manifest: dict):
    '''
    Load the downloaded dataset on memory and execute the preprocessing scripts on it.
    '''

    try:
        (train_set, test_set) = training.data_preprocessing(file_name, dataset_path,
                                                            manifest['dataset_params']['preprocessor']['content'])

        return train_set, test_set
    except Exception:
        logger.error(
            f'Failed to run Dataset Proprocessing. Aborting Process for [{job_name}] at cluster [{cluster_id}]!\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


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
