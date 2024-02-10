'''
Implementation of FedAvg Aggregator for Server Aggregation.
'''
import copy
import torch


def aggregator(model, client_params: list, client_weights: list, extra_data: dict, device='cpu', kwargs=None):
    """
    Performs weighted sum of the client parameters, and returns the new model. 
    """

    # if any extra_data and keyword arguments are passed
    _ = extra_data
    # _ = kwargs
    beta = kwargs['fed_avg_momentum']
    EXTRADATA_V = 'fedavgm_vmom'

    with torch.no_grad():

        # get the current global parameters
        global_params = model.state_dict()

        # define the next global parameters
        new_global_params = copy.deepcopy(global_params)  # Create a deep copy

        # also create the gradient
        gradient = copy.deepcopy(global_params)

        # Initialize global parameters to zeros
        for param_name, param in new_global_params.items():
            param = param.to(device)
            param.zero_()

        # Initialize v_momentum to zero if not already in extradata
        if 'fedavgm_vmom' not in extra_data:
            v_momenutm = copy.deepcopy(global_params)
            for param_name, param in v_momenutm.items():
                param = param.to(device)
                param.zero_()
        else:
            v_momenutm = extra_data[EXTRADATA_V]

        # Aggregate client updates (basically FedAvg)
        for client_state_dict, weight in zip(client_params, client_weights):
            for param_name, param in client_state_dict.items():
                # move client param to gpu
                param = param.to(device)

                new_global_params[param_name] += (weight * param).type(
                    new_global_params[param_name].dtype)

        # compute the gradient (dw = w_old - w_new)
        for param_name, param in new_global_params.items():
            global_params[param_name] = global_params[param_name].to(device)

            gradient[param_name] = torch.sub(
                global_params[param_name], new_global_params[param_name])

        # compute new v_momentum (v = beta.v + dw)
        for param_name, param in v_momenutm.items():
            v_momenutm[param_name] = torch.add((beta * param).type(
                new_global_params[param_name].dtype), gradient[param_name])

        # update v_momentum in extra_data
        extra_data[EXTRADATA_V] = v_momenutm

        # compute new global parameters (w_new = w_old - v)
        for param_name, param in new_global_params.items():
            new_global_params[param_name] = torch.sub(
                global_params[param_name], v_momenutm[param_name])

        # finally set new aggregated global parameters
        model.load_state_dict(new_global_params)

    return model


'''
1. Calculate the New Gradient from global params and new_global_params.
2. Create new v of shape global params, set to zero if not defined
3. Compute v from eq
4. Compute new aggregation parameters
'''
