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
    lambda_l, lambda_g = kwargs['fed_rwa']['lambda_l'], kwargs['fed_rwa']['lambda_g']
    _ = extra_data

    with torch.no_grad():

        # get the model parameters
        global_params = model.state_dict()

        cos = torch.nn.CosineSimilarity(dim=0)
        cos.to(device)

        # compute the local similarities of client parameters
        sim_l = [0.0 for _ in client_params]
        for m, theta_m in enumerate(client_params):
            for i, theta_i in enumerate(client_params):
                # skip if m and i client are same
                if m == i:
                    continue

                # compute the similarity of theta_m with theta_i
                sim, layers = 0.0, 0
                for param_name, param in theta_m.items():
                    param = param.to(device)
                    theta_i[param_name] = theta_i[param_name].to(device)

                    if torch.is_floating_point(param):
                        simt = cos(torch.unsqueeze(torch.flatten(param), dim=-1),
                                   torch.unsqueeze(torch.flatten(theta_i[param_name]), dim=-1))
                        sim += simt.item()
                        layers += 1

                sim /= float(layers)
                sim_l[m] += sim
            sim_l[m] /= float(len(client_params)-1)

        # compute the global similarity of the client parameters
        sim_g = [0.0 for _ in client_params]
        for m, theta_m in enumerate(client_params):
            # compute the similarity of theta_m with theta_i
            sim, layers = 0.0, 0
            for param_name, param in theta_m.items():
                global_params[param_name] = global_params[param_name].to(
                    device)

                if torch.is_floating_point(param):
                    simt = cos(torch.unsqueeze(torch.flatten(param), dim=-1),
                               torch.unsqueeze(torch.flatten(global_params[param_name]), dim=-1))
                    sim += simt.item()
                    layers += 1

            sim /= float(layers)
            sim_g[m] += sim

        # merge similarity vectors
        sim_t = [(lambda_l*sl)+(lambda_g*sg) for sl, sg in zip(sim_l, sim_g)]
        new_weights = [sim*w for sim, w in zip(sim_t, client_weights)]
        nw_sum = sum(new_weights)
        new_weights = [float(w)/nw_sum for w in new_weights]

        print(client_weights, new_weights)

        new_global_params = copy.deepcopy(global_params)  # Create a deep copy

        # Initialize global parameters to zeros
        for param_name, param in new_global_params.items():
            param = param.to(device)
            param.zero_()

        # Aggregate client updates
        for client_state_dict, weight in zip(client_params, new_weights):
            for param_name, param in client_state_dict.items():
                # move client param to gpu
                param = param.to(device)

                new_global_params[param_name] += (weight * param).type(
                    new_global_params[param_name].dtype)

        model.load_state_dict(new_global_params)

    return model
