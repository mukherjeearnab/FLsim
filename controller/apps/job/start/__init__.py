'''
Job Start Module
'''
import traceback
from time import sleep
from env import env
from state import job_config_state
from helpers.logging import logger
from helpers.file import read_yaml_file
from helpers.http import post
from apps.job.load.modules_loader import load_module_files
from apps.job.load.dataset_config import create_dist_tree


def start_job(job_name: str):
    '''
    Start a Job
    '''
    if job_name not in job_config_state:
        logger.error(f'Job {job_name} does not exist!')
        return

    # load the job config state
    job_config = job_config_state[job_name]
    logger.info(f'Retrieved Configuration Job {job_name}')

    logger.info('Uploading Job Configuration to LogiCon')

    try:
        res = post(f"{env['LOGICON_URL']}/job/create",
                   {'job_name': job_name, 'manifest': job_config['config']})

        logger.info(f"RESPONSE: {res['message']}")
    except Exception:
        logger.error(
            f'Failed to Create Job Instance!\n{traceback.format_exc()}')
        return

    sleep(env['DELAY'])

    logger.info('Starting Job Instance...')
    try:
        res = post(f"{env['LOGICON_URL']}/job/start",
                   {'job_name': job_name})

        logger.info(f"RESPONSE: {res['message']}")
    except Exception:
        logger.error(
            f'Failed to Start Job Instance!\n{traceback.format_exc()}')
