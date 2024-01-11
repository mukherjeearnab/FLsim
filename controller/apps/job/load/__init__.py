'''
Job Load Module
'''
import json
from state import job_config_state
from helpers.logging import logger
from helpers.file import read_yaml_file
from apps.job.load.modules_loader import load_module_files
from apps.job.load.dataset_config import create_dist_tree


def load_job(job_name: str, job_config: str):
    '''
    Load the Job Config and perform some preliminary validation.
    '''
    # load the job config file
    config = read_yaml_file(f'../templates/job/{job_config}.yaml')

    logger.info(f'Reading Job Config: \n{job_config}')

    # job_config_state[job_name] = config

    # 1. read all the python modules and populate the dictionary
    config = load_module_files(config)

    # print(json.dumps(config, indent=4))

    # 2. append additional information and properties job configs
    root_cluster_id, dataset_structure = create_dist_tree(config)

    print(root_cluster_id, json.dumps(dataset_structure, indent=4))

    # 3. prepare and send details to dataset distributor to prepare dataset chunks for clients
