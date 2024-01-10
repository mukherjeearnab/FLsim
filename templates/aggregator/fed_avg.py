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
    _ = kwargs

    with torch.no_grad():

        # get the model parameters
        global_params = model.state_dict()

        new_global_params = copy.deepcopy(global_params)  # Create a deep copy

        # Initialize global parameters to zeros
        for param_name, param in new_global_params.items():
            param = param.to(device)
            param.zero_()

        # Aggregate client updates
        for client_state_dict, weight in zip(client_params, client_weights):
            for param_name, param in client_state_dict.items():
                # move client param to gpu
                param = param.to(device)

                new_global_params[param_name] += (weight * param).type(
                    new_global_params[param_name].dtype)

        model.load_state_dict(new_global_params)

    return model
