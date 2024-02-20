'''
DistLearn Strategy for Tensorflow Workflow
'''
import torch
from templates.strategy.base.learn_strategy import LearnStrategyBase
from templates.dataset.base.tensorflow_dataset_base import TensorflowDatasetBase


class TensorflowStrategyBase(LearnStrategyBase):
    '''
    Class for Strategy Base for Tensorflow-based training
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, dataset_params, is_local, device, base64_state)

        self.dataset = TensorflowDatasetBase(dataset_params)

    def load_dataset(self, train_set, test_set):
        '''
        Load the training and testing datasets
        '''

        if train_set is not None:
            # create the dataset loaders
            self._train_set = self.dataset.load_dataset(
                train_set, self.train_batch_size)

        self._test_set = self.dataset.load_dataset(
            test_set, self.test_batch_size)

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''

        raise NotImplementedError

    def train(self) -> None:
        '''
        Executes CrossEntropyLoss and Adam based Loop
        '''

        raise NotImplementedError

    def test(self) -> dict:
        '''
        Tests the model using the test loader, and returns the metrics as a dict
        '''

        raise NotImplementedError

    def aggregate(self):
        '''
        Implementaion of the FedAvg Aggregation Algorithm for this strategy.
        '''

        raise NotImplementedError

    def append_client_object(self, bash64_state: str, client_weight: float) -> None:
        '''
        Append client objects from their base64 state strings
        '''

        raise NotImplementedError

    @staticmethod
    def __get_metrics(actuals: list, preds: list) -> dict:
        '''
        Returns a dictionary of evaluation metrics.
        accuracy, precision, recall, f-1 score, f-1 macro, f-1 micro, confusion matrix
        '''

        raise NotImplementedError
