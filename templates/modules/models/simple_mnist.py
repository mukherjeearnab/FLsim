'''
Sample Neural Network Module using the MNSIT dataset
'''
import torch
import torch.nn as nn


class ModelClass(nn.Module):
    def __init__(self):
        super(ModelClass, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)  # Flatten the input images
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
