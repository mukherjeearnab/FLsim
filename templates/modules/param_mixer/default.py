'''
Global+Local Parameter Mixer Module
'''
from copy import deepcopy


def param_mixer(current_global_params: dict, previous_local_params: dict) -> dict:
    '''
    This Param Mixer will do nothing and replace the previous local parameters
    with the current global parameters.
    '''

    # replace the previous parameter layer weights with the current global ones
    # for param_key in previous_local_params.keys():
    #     previous_local_params[param_key] = deepcopy(
    #         current_global_params[param_key])

    return current_global_params
