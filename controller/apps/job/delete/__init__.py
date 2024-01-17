'''
Job Delete Module
'''
import traceback
from env import env
from state import job_config_state
from helpers.logging import logger
from helpers.http import post, get


def delete_job(job_name: str):
    '''
    Delete a Job
    '''
    if job_name not in job_config_state:
        logger.error(f'Job {job_name} does not exist!')
        return

    logger.info(
        'Sending DEL Request to Dataset Distributor for Job {job_name}')
    try:
        res = get(f"{env['DATADIST_URL']}/delete",
                  {'job_name': job_name})

        logger.info(f"Dataset Delete Status: {res['status']}")
    except Exception:
        logger.error(
            f'Failed to Delete Dataset Instance!\n{traceback.format_exc()}')

    logger.info('Sending DEL Request to LogiCon for Job {job_name}')
    try:
        res = post(f"{env['LOGICON_URL']}/job/delete",
                   {'job_name': job_name})

        logger.info(f"RESPONSE: {res['message']}")
        del job_config_state[job_name]
    except Exception:
        logger.error(
            f'Failed to Delete Job Instance!\n{traceback.format_exc()}')
