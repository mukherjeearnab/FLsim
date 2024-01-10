'''
ResNet50 Neural Network Module for Breast Density Prediction
'''

import torch.nn as nn
import torchvision.models as models
# from torchvision.models import ResNet18_Weights


class ModelClass(nn.Module):
    def __init__(self):
        super(ModelClass, self).__init__()
        # Load the pre-trained ResNet-50 model
        # weights=ResNet18_Weights.IMAGENET1K_V1)
        self.resnet18 = models.resnet18()
        # self.resnet18.conv1 = nn.Conv2d(1, 64, kernel_size=(
        #     7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        num_features = self.resnet18.fc.in_features
        self.resnet18.fc = nn.Linear(num_features, 10)

    def forward(self, x):
        x = self.resnet18(x)
        # x = self.sigmoid(x)
        # print("SIGMOID OUT", x)
        return x
