import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Fully connected layers
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.proj = nn.Linear(512, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(512, 10)  # 10 classes for CIFAR-10

    def forward(self, x):
        x = self.relu1(self.conv1(x))
        x = self.pool(x)
        x = self.relu2(self.conv2(x))
        x = self.pool(x)

        # Flatten before the fully connected layers
        x = x.view(-1, 128 * 8 * 8)

        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

    def forward_with_projection(self, x):
        x = self.relu1(self.conv1(x))
        x = self.pool(x)
        x = self.relu2(self.conv2(x))
        x = self.pool(x)

        # Flatten before the fully connected layers
        x = x.view(-1, 128 * 8 * 8)

        x = self.fc1(x)
        z = self.proj(x)
        y = self.fc2(self.relu3(x))
        return z, y


ModelClass = SimpleCNN
