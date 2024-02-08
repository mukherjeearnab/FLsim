'''
Sample Dataset Preperation Module for MNSIT dataset
This module is executed before the client distribution 
for the dataset is performed in the Data Warehouse.
'''
import numpy as np
import torchvision
import torchvision.transforms as transforms


def prepare_dataset():
    '''
    Prepare the CIFAR10 Dataset here for Distribution to Clients
    NOTE: Returns the Train Set as the complete dataset.
    '''

    # load the train dataset
    train_dataset = torchvision.datasets.MNIST(
        root='./datasets', train=True, download=True)

    train_data, train_labels = train_dataset.data.numpy(), train_dataset.targets.numpy()

    # load the test dataset
    test_dataset = torchvision.datasets.MNIST(
        root='./datasets', train=False, download=True)

    # obtain the data and label tensors
    test_data, test_labels = test_dataset.data.numpy(), test_dataset.targets.numpy()

    # return the tuple as ((train_data, train_labels), (test_data, test_labels)),
    # else if not test set, then ((train_data, train_labels), None)
    # on passing None, the server will split the train dataset into train and test, based on the train-test ratio
    return ((train_data, train_labels), (test_data, test_labels))
