'''
Job Root Module
'''
import traceback
from time import sleep
from env import env
from helpers.logging import logger
from apps.job.check_launch import get_jobs_from_server


def job_keep_alive_process():
    '''
    Keep ALive process to launch job getters every time-interval
    '''
    logger.info('Job keep alive process started.')

    # the infinite loop
    while True:
        try:
            get_jobs_from_server(env['LOGICON_URL'])
        except Exception:
            logger.error(
                f'Failed to fetch job list from LogiCon! {traceback.format_exc()}')

        sleep(env['DELAY']*4)
