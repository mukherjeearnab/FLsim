'''
MobileNet Neural Network Module for Breast Density Prediction
'''

import torchvision.models as models
import torch
import torch.nn as nn


class ModelClass(nn.Module):
    def __init__(self):
        super(ModelClass, self).__init__()

        self.mobilenet = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

        # Change the input channel to 1
        self.mobilenet.features[0][0] = nn.Conv2d(1, 32, kernel_size=(
            3, 3), stride=(2, 2), padding=(1, 1), bias=False)

        # Remove the last fully connected layer
        self.mobilenet.classifier = nn.Sequential()

        # Remove the global average pooling layer
        self.mobilenet.avgpool = nn.Identity()

        # Define a dropout layer
        # Adjust the dropout probability as needed (e.g., p=0.5 for 50% dropout)
        self.dropout = nn.Dropout(p=0.5)

        # Define a global average pooling layer
        self.global_avg_pooling = nn.AdaptiveAvgPool2d((1, 1))
        # self.global_avg_pooling = GlobalAvgPool()

        # Define a convolutional layer with 512 output channels and 1x1 kernel
        self.conv1x1_2 = nn.Conv2d(
            in_channels=1280, out_channels=1, kernel_size=1)

        self.flatten = nn.Flatten()

        # Define the sigmoid activation for binary classification
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.mobilenet.features(x)
        # print(x.size())
        x = self.global_avg_pooling(x)
        x = self.dropout(x)
        x = self.conv1x1_2(x)
        x = self.flatten(x)
        x = self.sigmoid(x)
        return x
