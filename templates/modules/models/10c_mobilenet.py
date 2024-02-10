'''
MobileNet Neural Network Module for Breast Density Prediction
'''

import torchvision.models as models
import torch.nn as nn


class MobileNet(nn.Module):
    def __init__(self):
        super(MobileNet, self).__init__()

        # weights=models.MobileNet_V2_Weights.IMAGENET1K_V1
        self.mobilenet = models.mobilenet_v2()
        self.mobilenet.classifier[-1] = nn.Linear(
            self.mobilenet.classifier[-1].in_features, 10)

    def forward(self, x):
        x = self.mobilenet(x)

        return x


ModelClass = MobileNet
