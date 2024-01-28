'''
Job Abort Module
'''
import traceback
from env import env
from helpers.logging import logger
from helpers.http import post


def abort_job(job_name: str):
    '''
    Abort a Job
    '''
    logger.info(f'Sending Abort Signal to LogiCon for Job {job_name}')

    try:
        res = post(f"{env['LOGICON_URL']}/job/set_abort",
                   {'job_name': job_name})

        logger.info(f"RESPONSE: {res['message']}")
    except Exception:
        logger.error(
            f'Failed to Abort Job Instance!\n{traceback.format_exc()}')
