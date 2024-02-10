'''
DistLearn Dataset Definition Class for PyTorch
'''
import torch
import torch.utils.data as data_utils
from templates.dataset.base.dataset_base import DatasetBase


class TorchDatasetBase(DatasetBase):
    '''
    Base Class for Dataset Definition
    '''

    def __init__(self, dataset_params: dict):
        super().__init__(dataset_params)

    def prepare_root_dataset(self):
        '''
        Method to prepare the dataset root dataset and return it as a tuple of:

        ((train_data, train_labels), (test_data, test_labels))
        '''

        raise NotImplementedError

    def distribute_into_chunks(self):
        '''
        Distribute the Root Dataset into client chunks using a distribution algorithm

        returns: client_chunks (data, labels), new_client_weights
        '''

        raise NotImplementedError

    def train_test_split_method(self, dataset: tuple):
        '''
        Creates train and test sets by splitting the original dataset into 
        len(split_weights) chunks.

        Input: dataset (type: tuple) as (data, labels)

        Output: train_test_sets (type: tuple) as [((train_data, train_labels), (test_data, test_labels))]
        '''

        '''
        Creates train and test sets by splitting the original dataset into 
        len(split_weights) chunks.
        '''

        data, labels = dataset

        total_data_samples = len(data)

        # calculate the split sections
        split_sections = [int(total_data_samples*weight)
                          for weight in self.train_test_split]

        if sum(split_sections) < total_data_samples:
            split_sections[-1] += total_data_samples - sum(split_sections)
        else:
            split_sections[0] -= sum(split_sections) - total_data_samples

        # split the data and labels into chunks
        data_chunks = torch.split(data, split_size_or_sections=split_sections)
        label_chunks = torch.split(
            labels, split_size_or_sections=split_sections)

        # create dataset tuples for train and test chunks
        train_test_chunks = []
        for i in range(len(self.train_test_split)):
            split_chunk = (data_chunks[i], label_chunks[i])

            train_test_chunks.append(split_chunk)

        # returns (train_set, test_set)
        return (train_test_chunks[0], train_test_chunks[1])

    def load_dataset(self, dataset, batch_size: int):
        '''
        Load Dataset after reading it's pickle from file
        What it does is creates torch data loaders for the dataset
        '''

        return self._tensor_to_data_loader(dataset, batch_size)

    @staticmethod
    def concatenate_method(tensors: list):
        '''
        Method to concatenate multiple tensors of data or labels

        Useful to create global test / train sets
        '''

        return torch.cat(tensors, 0)

    def preprocess_data(self):
        '''
        Preprocess dataset at client / server side
        '''

        raise NotImplementedError

    @staticmethod
    def _tensor_to_data_loader(dataset: tuple, batch_size: int):
        '''
        convert dataset tensor to data loader object
        '''

        data, labels = dataset

        train = data_utils.TensorDataset(data, labels)
        train_loader = data_utils.DataLoader(
            train, batch_size, shuffle=True, num_workers=2)

        return train_loader
