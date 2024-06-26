'''
DistLearn Strategy for SKLearn Workflow
'''
import torch
from templates.strategy.base.learn_strategy import LearnStrategyBase
from templates.dataset.base.sklearn_dataset_base import SKLearnDatasetBase


class SKLearnStrategyBase(LearnStrategyBase):
    '''
    Class for Strategy Base for SKLearn-based training
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, dataset_params, is_local, device, base64_state)

        self.dataset = SKLearnDatasetBase(dataset_params)

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''

        raise NotImplementedError

    def train(self, train_loader: torch.utils.data.DataLoader) -> None:
        '''
        Executes CrossEntropyLoss and Adam based Loop
        '''

        raise NotImplementedError

    def test(self, test_loader: torch.utils.data.DataLoader) -> dict:
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
