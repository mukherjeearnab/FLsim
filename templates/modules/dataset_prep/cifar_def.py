'''
Sample Dataset Preperation Module for MNSIT dataset
This module is executed before the client distribution 
for the dataset is performed in the Data Warehouse.
'''
import torch
import torchvision
import torchvision.transforms as transforms


def prepare_torch_dataset():
    '''
    Prepare the CIFAR10 Dataset here for Distribution to Clients
    NOTE: Returns the Train Set as the complete dataset.
    '''

    # Load and preprocess the dataset
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])

    # load the train dataset
    train_dataset = torchvision.datasets.CIFAR10(
        root='./datasets', train=True, transform=transform, download=True)
    # Create data loaders
    train_loader = torch.utils.data.DataLoader(
        dataset=train_dataset, batch_size=len(train_dataset), shuffle=False)
    # obtain the data and label tensors
    train_data, train_labels = next(iter(train_loader))

    # load the test dataset
    test_dataset = torchvision.datasets.CIFAR10(
        root='./datasets', train=False, transform=transform, download=True)
    # Create data loaders
    test_loader = torch.utils.data.DataLoader(
        dataset=test_dataset, batch_size=len(test_dataset), shuffle=False)
    # obtain the data and label tensors
    test_data, test_labels = next(iter(test_loader))

    # return the tuple as ((train_data, train_labels), (test_data, test_labels)),
    # else if not test set, then ((train_data, train_labels), None)
    # on passing None, the server will split the train dataset into train and test, based on the train-test ratio
    return ((train_data, train_labels), (test_data, test_labels))
