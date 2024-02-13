'''
Sample C Neural Network Module using the CIFAR dataset
From https://medium.com/analytics-vidhya/classifying-cifar-10-using-a-simple-cnn-4e9a6dd7600b
'''
import torch.nn as nn


class CIFAR10SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(3, 3),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten()
        )

        self.projection_head = nn.Sequential(
            nn.Linear(1024, 128)
        )

        self.classification_head = nn.Sequential(
            nn.Linear(1024, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )

    def forward(self, x):
        x = self.network(x)
        return self.classification_head(x)

    def forward_with_projection(self, x):
        x = self.network(x)
        proj = self.projection_head(x)
        pred = self.classification_head(x)

        return proj, pred
