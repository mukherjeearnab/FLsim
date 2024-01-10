'''
Simple Neural Network Training Loop Module
'''
from copy import deepcopy
import torch
import torch.nn as nn
import torch.optim as optim


def train_loop(num_epochs: int, learning_rate: float,
               train_loader: torch.utils.data.dataloader.DataLoader,
               local_model, global_model, prev_local_model,
               extra_params: dict, extra_data: dict, device='cpu') -> None:
    '''
    The Training Loop Function. It trains the local_model of num_epochs.
    '''

    # hyperparameters
    w_dis = extra_params['mdis']['w_dis']['init']
    w_dis_max = extra_params['mdis']['w_dis']['max']
    w_dis_min = extra_params['mdis']['w_dis']['min']
    decay_step = extra_params['mdis']['w_dis']['decay']['step']
    decay_wait = extra_params['mdis']['w_dis']['decay']['wait']

    # extra_data
    extra_data['loss_history'] = {"prev": float(
        'inf'), "redn_count": 0} if 'loss_history' not in extra_data else extra_data['loss_history']
    extra_data['w_dis'] = w_dis if 'w_dis' not in extra_data else extra_data['w_dis']

    print(extra_data['w_dis'])

    # move the local_model to the device, cpu or gpu
    local_model = local_model.to(device)
    global_model = global_model.to(device)
    prev_local_model = prev_local_model.to(device)

    if 'prev_globals' not in extra_data:
        extra_data['prev_globals'] = list()
    else:
        if len(extra_data['prev_globals']) > extra_params['mdis']['pre_params']['global']:
            extra_data['prev_globals'] = extra_data['prev_globals'][1:]
        extra_data['prev_globals'].append(deepcopy(global_model))

    if 'prev_locals' not in extra_data:
        extra_data['prev_locals'] = [deepcopy(prev_local_model)]
    else:
        if len(extra_data['prev_locals']) > extra_params['mdis']['pre_params']['local']:
            extra_data['prev_locals'] = extra_data['prev_locals'][1:]
        extra_data['prev_locals'].append(deepcopy(prev_local_model))

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(local_model.parameters(), lr=learning_rate)
    cos = torch.nn.CosineSimilarity(dim=-1)

    # Epoch loop
    for epoch in range(num_epochs):
        local_model.train()
        total_loss = 0.0

        w_mdis = 0.0 if epoch == 0 else extra_data['w_dis']

        for i, (inputs, labels) in enumerate(train_loader, 1):

            # move tensors to the device, cpu or gpu
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            proj_l, pred_l = local_model.forward_with_projection(inputs)
            proj_g, _ = global_model.forward_with_projection(inputs)

            posi = cos(proj_l, proj_g)
            logits = posi.reshape(-1, 1)

            for model in extra_data['prev_globals']:
                # model.to(device)
                proj, _ = model.forward_with_projection(inputs)
                nega = cos(proj_l, proj)
                logits = torch.cat((logits, nega.reshape(-1, 1)), dim=1)
                # model.to('cpu')

            for model in extra_data['prev_locals']:
                # model.to(device)
                proj, _ = model.forward_with_projection(inputs)
                nega = cos(proj_l, proj)
                logits = torch.cat((logits, nega.reshape(-1, 1)), dim=1)
                # model.to('cpu')

            logits = logits.to(device)
            logits /= 0.5

            mask = torch.zeros(inputs.size(0)).long()
            mask = mask.to(device)

            con_loss = w_mdis * criterion(logits, mask)

            sup_loss = criterion(pred_l, labels)

            loss = sup_loss + con_loss

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            print(f'Processing Batch {i}/{len(train_loader)}.', end='\r')

        average_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Loss: {average_loss:.4f}")

        if epoch == 0:
            if average_loss < extra_data['loss_history']['prev']:
                if extra_data['loss_history']['redn_count'] >= decay_wait:
                    extra_data['w_dis'] -= decay_step
                    if extra_data['w_dis'] < w_dis_min:
                        extra_data['w_dis'] = w_dis_min
                else:
                    extra_data['loss_history']['redn_count'] += 1
            else:
                extra_data['loss_history']['redn_count'] = 0
                extra_data['w_dis'] += decay_step
                if extra_data['w_dis'] >= w_dis_max:
                    extra_data['w_dis'] = w_dis_max

            extra_data['loss_history']['prev'] = average_loss
