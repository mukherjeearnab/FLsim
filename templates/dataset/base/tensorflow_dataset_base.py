'''
DistLearn Dataset Definition Class for Tensorflow
'''
import numpy
from templates.dataset.base.dataset_base import DatasetBase


class TensorflowDatasetBase(DatasetBase):
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

        split_boundary = [total_data_samples * self.train_test_split[0]]

        # split the data and labels into chunks
        data_chunks = numpy.split(
            data, split_size_or_sections=split_boundary)
        label_chunks = numpy.split(
            labels, split_size_or_sections=split_boundary)

        # create dataset tuples for train and test chunks
        train_test_chunks = []
        for i in range(len(self.train_test_split)):
            split_chunk = (data_chunks[i], label_chunks[i])

            train_test_chunks.append(split_chunk)

        # returns (train_set, test_set)
        return (train_test_chunks[0], train_test_chunks[1])

    def load_dataset(self, dataset):
        '''
        Load Dataset after reading it's pickle from file
        What it does is creates torch data loaders for the dataset
        '''

        return dataset

    @staticmethod
    def concatenate_method(tensors: list):
        '''
        Method to concatenate multiple tensors of data or labels

        Useful to create global test / train sets
        '''

        return numpy.concatenate(tensors, 0)

    def preprocess_data(self, train_tuple, test_tuple):
        '''
        Preprocess dataset at client / server side
        '''

        raise NotImplementedError
