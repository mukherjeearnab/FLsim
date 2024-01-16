'''
Aggregation Process Module
'''
import traceback
from env import env
from helpers.argsparse import args
from helpers.logging import logger
from helpers.dynamod import load_module
from helpers.torch import get_device
from apps.common.setters import _fail_exit

datadist_url = env['DATADIST_URL']
node_id = args['node_id']


def aggregate_client_params(job_name: str, cluster_id: str, node_type: str, manifest: dict,
                            global_model, client_params: dict, extra_data: dict):
    '''
    The Aggregation Process Executor
    '''
    device = get_device()
    global_model = global_model.to(device)

    # load the model module
    try:
        aggregator_module = load_module(
            'agg_module', manifest['aggregator_params']['aggregator']['content'])
    except Exception:
        logger.info(
            f'Error loading Aggregator Module. Terminating...\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)

    # arrange the params, weights and extra_data into lists
    client_param_list, client_weight_list, client_extra_data = [], [], []
    for _, payload in client_params.items():
        client_param_list.append(payload['param'])
        client_weight_list.append(payload['weight'])
        client_extra_data.append(payload['extra_data'])

    extra_data['client_extra_data'] = client_extra_data

    # run the aggregator function and obtain new global model
    try:
        global_model = aggregator_module.aggregator(global_model, client_param_list, client_weight_list,
                                                    extra_data, device, manifest['aggregator_params']['extra_params'])

        return global_model
    except Exception:
        logger.info(
            f'Error Executing Aggregator. Terminating...\n{traceback.format_exc()}')
        _fail_exit(job_name, cluster_id, node_type)
