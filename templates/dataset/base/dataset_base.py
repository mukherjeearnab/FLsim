'''
DistLearn Dataset Definition Base Class
'''


class DatasetBase(object):
    '''
    Base Class for Dataset Definition
    '''

    def __init__(self, dataset_params: dict):

        self.dataset_download_dir = './datasets'

        self.client_weights = dataset_params['chunks'] if 'chunks' in dataset_params else None

        # if the distribution weights cannot be predetermined
        self.dynamic_weights = True if self.client_weights is None else False

        self.extra_params = dataset_params['extra_params'] if 'extra_params' in dataset_params else None

        self.train_test_split = dataset_params['train_test_split'] if 'train_test_split' in dataset_params else [
            0.8, 0.2]

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

        Output: train_test_sets (type: list) as [((train_data, train_labels), (test_data, test_labels))]
        '''

        raise NotImplementedError

    @staticmethod
    def load_dataset():
        '''
        Load Dataset after reading it's pickle from file
        '''

        raise NotImplementedError

    @staticmethod
    def concatenate_method(tensors: list):
        '''
        Method to concatenate multiple tensors of data or labels

        Useful to create global test / train sets
        '''

        raise NotImplementedError

    def preprocess_data(self):
        '''
        Preprocess dataset at client / server side
        '''

        raise NotImplementedError
