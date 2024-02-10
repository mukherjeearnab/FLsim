'''
Simple Neural Network Training Loop Module
'''
import torch
import torch.nn as nn
import torch.optim as optim


def train_loop(num_epochs: int, learning_rate: float,
               train_loader: torch.utils.data.dataloader.DataLoader,
               local_model, global_model, prev_local_model,
               extra_params: dict, device='cpu') -> None:
    '''
    The Training Loop Function. It trains the model of num_epochs.
    '''
    _ = prev_local_model
    _ = global_model
    _ = extra_params

    # move the local_model to the device, cpu or gpu
    local_model = local_model.to(device)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(local_model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        local_model.train()
        total_loss = 0.0

        for i, (inputs, labels) in enumerate(train_loader, 1):

            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = local_model(inputs)
            loss = criterion(outputs, labels.unsqueeze(1).float())
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            print(f'Processing Batch {i}/{len(train_loader)}.', end='\r')

        average_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Loss: {average_loss:.4f}")
