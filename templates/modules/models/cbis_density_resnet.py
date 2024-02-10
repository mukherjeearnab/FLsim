'''
ResNet50 Neural Network Module for Breast Density Prediction
'''

import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights


class ModelClass(nn.Module):
    def __init__(self):
        super(ModelClass, self).__init__()
        # Load the pre-trained ResNet-50 model
        # weights=ResNet50_Weights.IMAGENET1K_V1)
        self.resnet50 = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.resnet50.conv1 = nn.Conv2d(1, 64, kernel_size=(
            7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        num_features = self.resnet50.fc.in_features
        self.resnet50.fc = nn.Linear(num_features, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.resnet50(x)
        x = self.sigmoid(x)
        # print("SIGMOID OUT", x)
        return x
