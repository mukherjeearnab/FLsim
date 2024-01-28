'''
Job Load Module
'''
import os
import shutil
import traceback
from env import env
from state import job_config_state
from helpers.logging import logger
from helpers.file import read_yaml_file, exists
from helpers.http import post
from apps.job.load.modules_loader import load_module_files
from apps.job.load.dataset_config import create_dist_tree


def load_job(job_name: str, job_config: str):
    '''
    Load the Job Config and perform some preliminary validation.
    '''

    logger.info(f'Updating Templates Cache.')
    # copy over the templates directory
    temp_src = '../templates'
    temp_dest = './templates'
    if os.path.exists(temp_dest):
        shutil.rmtree(temp_dest)
    shutil.copytree(temp_src, temp_dest)

    config_file = f'./templates/job/{job_config}.yaml'

    if not exists(config_file):
        logger.error('Job Config file [{job_config}.yaml] not found!')
        return

    # load the job config file
    config = read_yaml_file(config_file)

    with open(config_file, 'r', encoding='utf8') as f:
        raw_config = f.read()

    logger.info(f'Reading Job Config: {job_config}')

    # job_config_state[job_name] = config

    # 1. read all the python modules and populate the dictionary
    try:
        config = load_module_files(config)
        logger.info('Loaded Py Modules from Job Config')
    except Exception:
        logger.error(
            f'Error loading Job Py Modules!\n{traceback.format_exc()}')
        return

    # 2. append additional information and properties job configs
    # Nothing here yet

    # 3. prepare and send details to dataset distributor to prepare dataset chunks for clients
    logger.info(f'Starting Dataset Preperation for Job {job_name}')
    try:
        _, dataset_manifest = create_dist_tree(config)
        res = post(f"{env['DATADIST_URL']}/prepare",
                   {'job_name': job_name, 'manifest': dataset_manifest})
        logger.info(f'Dataset Preperation Complete for Job {job_name}')

        dist_metadata = res['metadata']
    except Exception:
        logger.error(
            f'Error Preparing Dataset!\n{traceback.format_exc()}')
        return

    # add job config details to state variable
    job_config_state[job_name] = {
        'config': config,
        'dataset_manifest': dataset_manifest,
        'raw_config': raw_config,
        'dist_metadata': dist_metadata
    }

    logger.info(f'Loading Job Complete for Job {job_name}')
