'''
Python Modules Loader for Jobs
'''
import os
import ast
import dill
import json
import base64
import importlib
from helpers.file import read_py_module


def load_module_files(config: dict):
    '''
    Load all the modules files present in the given job config
    '''

    detached_config = json.loads(json.dumps(config))

    detached_config['templates'] = set()

    client_module_loader(detached_config)
    worker_module_loader(detached_config)
    cluster_module_loader(detached_config)

    detached_config['templates'] = list(detached_config['templates'])

    return detached_config


def client_module_loader(config: dict):
    '''
    Module Loader for Client Configs
    '''

    for client_id in config['clients'].keys():
        load_model_params(
            config['clients'][client_id]['model_params'], config['templates'])
        load_train_params(
            config['clients'][client_id]['train_params'], config['templates'])
        load_dataset_params(
            config['clients'][client_id]['dataset_params'], config['templates'])


def worker_module_loader(config: dict):
    '''
    Module Loader for Worker Configs
    '''

    for worker_id in config['workers'].keys():
        load_model_params(
            config['workers'][worker_id]['model_params'], config['templates'])
        load_aggregator_params(
            config['workers'][worker_id]['aggregator_params'], config['templates'])
        load_dataset_params(
            config['workers'][worker_id]['dataset_params'], config['templates'])


def cluster_module_loader(config: dict):
    '''
    Module Loader for Cluster Configs
    '''

    for cluster_id in config['clusters']:
        load_consensus_params(
            config['clusters'][cluster_id]['consensus_params'], config['templates'])
        load_dataset_params(
            config['clusters'][cluster_id]['dataset_params'], config['templates'])
        config['clusters'][cluster_id]['train_params']['rounds'] = config['job_params']['rounds']


def load_model_params(config: dict, template_set: set):
    '''
    FL Model Modules Loader
    '''

    # load the model file
    config['strategy'] = {
        'file': config['strategy'],
        'definition': dump_strategy_definition(config['strategy']),
        'deps': get_dependencies(f"./templates/strategy/{config['strategy']}.py")
    }

    for template in config['strategy']['deps']:
        template_set.add(template)


def load_train_params(config: dict, template_set: set):
    '''
    FL Client Training Modules Loader
    '''
    _ = config


def load_aggregator_params(config: dict, template_set: set):
    '''
    FL Aggregator Modules Loader
    '''
    _ = config


def load_dataset_params(config: dict, template_set: set):
    '''
    FL Dataset Modules Loader
    '''
    # load the dataset prep file
    file = f"./templates/dataset_prep/{config['prep']}"
    config['prep'] = {
        'file': config['prep'],
        'content': read_py_module(file)
    }
    template_set.add(file)

    # load the dataset preprocessor file
    file = f"./templates/preprocessor/{config['preprocessor']}"
    config['preprocessor'] = {
        'file': config['prep'],
        'content': read_py_module(file)
    }
    template_set.add(file)

    # load the dataset distributor file
    file = f"./templates/distribution/{config['distribution']['distributor']}"

    config['distribution']['distributor'] = {
        'file': config['distribution']['distributor'],
        'content': read_py_module(file)
    }
    template_set.add(file)


def load_consensus_params(config: dict, template_set: set):
    '''
    FL Multi-worker Consensus Modules Loader
    '''

    # load the dataset distributor file
    file = f"./templates/consensus/{config['runnable']}"
    config['runnable'] = {
        'file': config['runnable'],
        'content': read_py_module(file)
    }
    template_set.add(file)


def dump_strategy_definition(strategy_name: str):
    '''
    Load the Strategy Definition as a module and extract the class definition
    and pickle using dill and return the base64 representation
    '''
    module_name = f'templates.strategy.{strategy_name}'

    strategy_module = importlib.import_module(module_name)

    class_def = strategy_module.StrategyDefinition

    def_bytes = dill.dumps(class_def)

    def_b64str = base64.b64encode(def_bytes).decode('utf8')

    return def_b64str


def get_dependencies(file_path: str) -> str:
    '''
    Get the template dependencies for a given strategy in templates
    '''

    def read_py_files(filename):
        py_files = []

        # Read the content of the main .py file
        with open(filename, 'r') as f:
            content = f.read()
            py_files.append(filename)

        # Parse the AST of the main .py file to find imported modules
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name

                    if 'templates' not in module_name:
                        continue

                    module_file = module_name + ".py"
                    if os.path.exists(module_file):
                        # Read the content of the imported module recursively
                        py_files.extend(read_py_files(module_file))
                    else:
                        print(f"Warning: Module '{module_name}' not found.")
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module

                if 'templates' not in module_name:
                    continue

                module_file = module_name.replace(".", os.sep) + ".py"
                if os.path.exists(module_file):
                    # Read the content of the imported module recursively
                    py_files.extend(read_py_files(module_file))
                else:
                    print(f"Warning: Module '{module_name}' not found.")

        return py_files

    deps = read_py_files(file_path)

    return deps
