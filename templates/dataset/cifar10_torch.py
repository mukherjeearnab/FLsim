'''
DistLearn Dataset Definition Class for PyTorch
'''
from templates.dataset.base.torch_dataset_base import TorchDatasetBase
from templates.modules.dataset_prep.cifar_def import prepare_torch_dataset
from templates.modules.distribution.diritchlet_dist import torch_distribute


class CIFAR10Dataset(TorchDatasetBase):
    '''
    CIFAR-10 Dataset Definition Class for PyTorch
    '''

    def __init__(self, dataset_params: dict):
        super().__init__(dataset_params)

        # declare the dataset name (should be unique and descriptive)
        self.dataset_name = 'cifar10_torch'

        # declare the dataset distribution algorithm / method
        # (algorithm that is used in self.distribute_into_chunks method)
        self.distribution_method = 'dirichlet_dist'

    def prepare_root_dataset(self):
        '''
        Method to prepare the dataset root dataset and return it as a tuple of:

        ((train_data, train_labels), (test_data, test_labels))
        '''

        self.root_dataset = prepare_torch_dataset()

        return self.root_dataset

    def distribute_into_chunks(self):
        '''
        Distribute the Root Dataset into client chunks using a distribution algorithm

        returns: client_chunks (data, labels), new_client_weights
        '''

        self.client_chunks, self.client_weights = torch_distribute(
            self.root_dataset, self.client_weights, self.extra_params)

        return self.client_chunks, self.client_weights

    def preprocess_data(self, train_tuple, test_tuple):
        '''
        Preprocess dataset at client / server side
        Input train / test tuple as (data, label)

        output = train / test tuple as (data, label)
        '''

        return train_tuple, test_tuple
