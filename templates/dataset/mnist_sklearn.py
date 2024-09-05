'''
DistLearn Dataset Definition Class for PyTorch
'''
from templates.dataset.base.sklearn_dataset_base import SKLearnDatasetBase
from templates.modules.dataset_prep.mnist_sklearn import prepare_dataset
from templates.modules.distribution.uniform_dist_sklearn import distribute_into_client_chunks


class MNISTDataset(SKLearnDatasetBase):
    '''
    MNIST Dataset Definition Class for SKLearn
    '''

    def __init__(self, dataset_params: dict):
        super().__init__(dataset_params)

        # declare the dataset name (should be unique and descriptive)
        self.dataset_name = 'mnist_sklearn'

        # declare the dataset distribution algorithm / method
        # (algorithm that is used in self.distribute_into_chunks method)
        self.distribution_method = 'uniform_dist'

    def prepare_root_dataset(self):
        '''
        Method to prepare the dataset root dataset and return it as a tuple of:

        ((train_data, train_labels), (test_data, test_labels))
        '''

        return prepare_dataset()

    def distribute_into_chunks(self, root_dataset):
        '''
        Distribute the Root Dataset into client chunks using a distribution algorithm

        returns: client_chunks (data, labels), new_client_weights
        '''

        client_chunks, self.client_weights = distribute_into_client_chunks(
            root_dataset, self.client_weights, self.extra_params)

        return client_chunks, self.client_weights

    def preprocess_data(self, train_tuple, test_tuple):
        '''
        Preprocess dataset at client / server side
        Input train / test tuple as (data, label)

        output = train / test tuple as (data, label)
        '''

        return train_tuple, test_tuple


# Dont forget to set this the alias as 'DatasetDefinition'
DatasetDefinition = MNISTDataset
