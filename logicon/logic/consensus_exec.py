'''
Consensus Execution Module
'''
import traceback
from typing import Tuple, Union
from logic.job import Job
from helpers.dynamod import load_module
from helpers.logging import logger


def exec_consensus(job: Job) -> Tuple[bool, str, Union[str, None]]:
    '''
    Function to execute consensus for a job and select the global model param
    '''

    # load the consensus module
    try:
        consensus_module = load_module(
            'consensus_mod', job.cluster_config['consensus_params']['runnable']['content'])
    except Exception:
        logger.info(
            f'Error loading Consensus Module. Aborting...\n{traceback.format_exc()}')
        return False, job.exec_params['initial_params'][0], None

    # organize the data
    params, extra_datas = [], []
    for _, payload in job.exec_params['worker_aggregated_params'].items():
        params.append(payload['param'])
        extra_datas.append(payload['extra_data'])

    # execute the consensus module
    try:
        new_param, extra_data = consensus_module.consensus(params, extra_datas)

        return True, new_param, extra_data
    except Exception:
        logger.info(
            f'Error Executing Consensus. Aborting...\n{traceback.format_exc()}')
        return False, job.exec_params['initial_params'][0], None
