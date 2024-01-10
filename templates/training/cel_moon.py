'''
Simple Neural Network Training Loop Module
'''
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

    _ = extra_data

    # hyperparameters
    temperature = extra_params['moon']['temp']
    mu = extra_params['moon']['mu']

    # move the local_model to the device, cpu or gpu
    local_model = local_model.to(device)
    global_model = global_model.to(device)
    prev_local_model = prev_local_model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(local_model.parameters(), lr=learning_rate)

    cos = torch.nn.CosineSimilarity(dim=-1)

    # Epoch loop
    for epoch in range(num_epochs):
        local_model.train()
        total_loss = 0.0

        for i, (inputs, labels) in enumerate(train_loader, 1):

            # move tensors to the device, cpu or gpu
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            proj_l, pred_l = local_model.forward_with_projection(inputs)
            proj_g, _ = global_model.forward_with_projection(inputs)
            proj_pl, _ = prev_local_model.forward_with_projection(inputs)

            posi = cos(proj_l, proj_g)
            logits = posi.reshape(-1, 1)
            nega = cos(proj_l, proj_pl)
            logits = torch.cat((logits, nega.reshape(-1, 1)), dim=1)
            logits = logits.to(device)

            logits /= temperature
            mask = torch.zeros(inputs.size(0)).long()
            mask = mask.to(device)

            contrastive_loss = mu * criterion(logits, mask)

            loss = criterion(pred_l, labels)
            loss += contrastive_loss

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            print(f'Processing Batch {i}/{len(train_loader)}.', end='\r')

        average_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Loss: {average_loss:.4f}")
