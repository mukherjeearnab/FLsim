'''
Setters for Job
'''
from time import sleep
import traceback
from env import env
from helpers.argsparse import args
from helpers.http import post
from helpers.logging import logger

logicon_url = env['LOGICON_URL']
DELAY = env['DELAY']
node_id = args['node_id']


def update_node_status(job_name: str, cluster_id: str, node_type: str, status: int, extra_data=None) -> None:
    '''
    Update Node Status for a for a given job at a given cluster
    node_type: str = [client, worker]
    '''
    if node_type == 'client':
        url = f'{logicon_url}/job/update_client_status'
    elif node_type == 'worker':
        url = f'{logicon_url}/job/update_worker_status'
    else:
        _fail_exit(job_name, cluster_id, node_type)

    while True:
        try:
            res = post(url, {'job_name': job_name, 'cluster_id': cluster_id, f'{node_type}_id': node_id,
                             'status': status, 'extra_data': extra_data})

            if not res['status']:
                logger.error(
                    f'[{node_type}]({status}) {res["message"]} job [{job_name}] cluster [{cluster_id}] node [{node_id}]')
                raise AssertionError(
                    f'[{node_type}]({status}) Failed to Update Node Status for job [{job_name}] cluster [{cluster_id}] node [{node_id}]')
            else:
                logger.success(
                    f'[{node_type}]({status}) {res["message"]} job [{job_name}] cluster [{cluster_id}] node [{node_id}]')

            break
        except Exception:
            logger.error(
                f'[{node_type}] Failed to update {node_type} status.\n{traceback.format_exc()}')
            # _fail_exit(job_name, cluster_id, node_type)

        sleep(DELAY*2)


def append_node_params(job_name: str, cluster_id: str, node_type: str, param: int, extra_data=None) -> None:
    '''
    Update Trained/Aggregated Node Params for a for a given job at a given cluster
    node_type: str = [client, worker]
    '''
    if node_type == 'client':
        url = f'{logicon_url}/job/append_client_params'
    elif node_type == 'worker':
        url = f'{logicon_url}/job/append_worker_params'
    else:
        _fail_exit(job_name, cluster_id, node_type)

    try:
        res = post(url, {'job_name': job_name, 'cluster_id': cluster_id, f'{node_type}_id': node_id,
                         'param': param, 'extra_data': extra_data})

        logger.info(
            f'[{node_type}] {res["message"]} job [{job_name}] cluster [{cluster_id}] node [{node_id}]')
    except Exception:
        logger.error(
            f'[{node_type}] Failed to upload {node_type} params.\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)


def _fail_exit(job_name: str, cluster_id: str, node_type: str):
    '''
    If Getter Method fails, terminate the client/worker process
    and exit
    '''

    # update node status and exit
    update_node_status(job_name, cluster_id, node_type, status=5)
    exit()
