'''
Job Load Module
'''
from env import env
from state import job_config_state
from helpers.logging import logger
from helpers.file import read_yaml_file
from helpers.http import post
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
    logger.info('Loaded Py Modules from Job Config')

    # 2. append additional information and properties job configs
    # Nothing here yet

    # 3. prepare and send details to dataset distributor to prepare dataset chunks for clients
    _, dataset_manifest = create_dist_tree(config)
    logger.info(f'Starting Dataset Preperation for Job {job_name}')
    post(f"{env['DATADIST_URL']}/prepare",
         {'job_name': job_name, 'manifest': dataset_manifest})
    logger.info(f'Dataset Preperation Complete for Job {job_name}')

    # add job config details to state variable
    job_config_state[job_name] = {
        'config': config,
        'dataset_manifest': dataset_manifest
    }

    logger.info(f'Loading Job Complete for Job {job_name}')
