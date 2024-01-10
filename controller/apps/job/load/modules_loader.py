'''
Python Modules Loader for Jobs
'''
import json
from helpers.file import read_py_module


def load_module_files(config: dict):
    '''
    Load all the modules files present in the given job config
    '''

    detached_config = json.loads(json.dumps(config))

    client_module_loader(detached_config)
    worker_module_loader(detached_config)
    cluster_module_loader(detached_config)

    return detached_config


def client_module_loader(config: dict):
    '''
    Module Loader for Client Configs
    '''

    for client_id in config['clients'].keys():
        load_model_params(
            config['clients'][client_id]['model_params'])
        load_train_params(
            config['clients'][client_id]['train_params'])
        load_dataset_params(
            config['clients'][client_id]['dataset_params'])


def worker_module_loader(config: dict):
    '''
    Module Loader for Worker Configs
    '''

    for worker_id in config['workers'].keys():
        load_model_params(
            config['workers'][worker_id]['model_params'])
        load_aggregator_params(
            config['workers'][worker_id]['aggregator_params'])
        load_dataset_params(
            config['workers'][worker_id]['dataset_params'])


def cluster_module_loader(config: dict):
    '''
    Module Loader for Cluster Configs
    '''

    for cluster_id in config['clusters']:
        load_consensus_params(
            config['clusters'][cluster_id]['consensus_params'])
        load_dataset_params(
            config['clusters'][cluster_id]['dataset_params'])


def load_model_params(config: dict):
    '''
    FL Model Modules Loader
    '''

    print(config['model_file'])

    # load the model file
    config['model_file'] = {
        'file': config['model_file'],
        'content': read_py_module(
            f"../templates/models/{config['model_file']}")
    }

    # load the parameter mixer file
    config['parameter_mixer'] = {
        'file': config['parameter_mixer'],
        'content': read_py_module(
            f"../templates/param_mixer/{config['parameter_mixer']}")
    }

    # load the training loop file
    config['training_loop_file'] = {
        'file': config['training_loop_file'],
        'content': read_py_module(
            f"../templates/training/{config['training_loop_file']}")
    }

    # load the test file
    config['test_file'] = {
        'file': config['test_file'],
        'content': read_py_module(
            f"../templates/testing/{config['test_file']}")
    }


def load_train_params(config: dict):
    '''
    FL Client Training Modules Loader
    '''
    _ = config


def load_aggregator_params(config: dict):
    '''
    FL Aggregator Modules Loader
    '''
    # load the aggregator file
    config['aggregator'] = {
        'file': config['aggregator'],
        'content': read_py_module(
            f"../templates/aggregator/{config['aggregator']}")
    }


def load_dataset_params(config: dict):
    '''
    FL Dataset Modules Loader
    '''
    # load the dataset prep file
    config['prep'] = {
        'file': config['prep'],
        'content': read_py_module(
            f"../templates/dataset_prep/{config['prep']}")
    }

    # load the dataset preprocessor file
    config['preprocessor'] = {
        'file': config['prep'],
        'content': read_py_module(
            f"../templates/preprocessor/{config['preprocessor']}")
    }

    # load the dataset distributor file
    config['distribution']['distributor'] = {
        'file': config['distribution']['distributor'],
        'content': read_py_module(
            f"../templates/distribution/{config['distribution']['distributor']}")
    }


def load_consensus_params(config: dict):
    '''
    FL Multi-worker Consensus Modules Loader
    '''

    # load the dataset distributor file
    config['runnable'] = {
        'file': config['runnable'],
        'content': read_py_module(
            f"../templates/consensus/{config['runnable']}")
    }
