'''
MobileNet Neural Network Module for Breast Density Prediction
'''

import torchvision.models as models
import torch.nn as nn


class MobileNetWithProjection(nn.Module):
    def __init__(self):
        super(MobileNetWithProjection, self).__init__()

        # weights=models.MobileNet_V2_Weights.IMAGENET1K_V1
        self.mobilenet = models.mobilenet_v2()
        self.mobilenet.classifier[-1] = nn.Identity()

        self.projector = nn.Linear(1280, 512)
        self.classifier = nn.Linear(1280, 10)

    def forward(self, x):
        f = self.mobilenet(x)
        y = self.classifier(f)

        return y

    def forward_with_projection(self, x):
        f = self.mobilenet(x)
        z = self.projector(f)
        y = self.classifier(f)

        return z, y


ModelClass = MobileNetWithProjection
