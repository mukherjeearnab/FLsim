'''
DistLearn Dataset Definition Class for PyTorch
'''
from templates.dataset.base.tensorflow_dataset_base import TensorflowDatasetBase
from templates.modules.dataset_prep.tensorflow.cifar10 import prepare_tf_dataset
from templates.modules.distribution.tensorflow.dirichlet_dist import tf_distribute


class CIFAR10Dataset(TensorflowDatasetBase):
    '''
    CIFAR-10 Dataset Definition Class for PyTorch
    '''

    def __init__(self, dataset_params: dict):
        super().__init__(dataset_params)

        # declare the dataset name (should be unique and descriptive)
        self.dataset_name = 'cifar10_tensorflow'

        # declare the dataset distribution algorithm / method
        # (algorithm that is used in self.distribute_into_chunks method)
        self.distribution_method = 'dirichlet_dist'

    def prepare_root_dataset(self):
        '''
        Method to prepare the dataset root dataset and return it as a tuple of:

        ((train_data, train_labels), (test_data, test_labels))
        '''

        return prepare_tf_dataset()

    def distribute_into_chunks(self, root_dataset):
        '''
        Distribute the Root Dataset into client chunks using a distribution algorithm

        returns: client_chunks (data, labels), new_client_weights
        '''

        client_chunks, self.client_weights = tf_distribute(
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
DatasetDefinition = CIFAR10Dataset
