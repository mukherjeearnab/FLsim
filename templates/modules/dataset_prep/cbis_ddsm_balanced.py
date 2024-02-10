'''
Sample Dataset Preperation Module for MNSIT dataset
This module is executed before the client distribution 
for the dataset is performed in the Data Warehouse.
'''
import torch
import torchvision
import torchvision.transforms as transforms


def prepare_dataset():
    '''
    Prepare the MNIST Dataset here for Distribution to Clients
    NOTE: Returns the Train Set as the complete dataset.
    '''

    # Load and preprocess the train dataset
    train_dataset = torch.load(
        '/DATA/arnab/Projects/cbis-ddsm/official-ddsm-density-train-sm.tuple')
    train_data, train_labels = train_dataset

    # Load and preprocess the test dataset
    test_dataset = torch.load(
        '/DATA/arnab/Projects/cbis-ddsm/official-ddsm-density-test-sm.tuple')
    test_data, test_labels = test_dataset

    # return the tuple as ((train_data, train_labels), (test_data, test_labels)),
    # else if not test set, then ((train_data, train_labels), None)
    # on passing none, the server will split the dataset into train and test, based on the train-test ratio
    return ((train_data, train_labels), (test_data, test_labels))
