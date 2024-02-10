'''
DistLearn Strategy for training CIFAR-10 on a simple CNN,
using FedAvg Aggregation
'''
import math
from copy import deepcopy
import torch
from sklearn import metrics
from templates.strategy.base.torch_strategy import TorchStrategyBase
from templates.dataset.cifar10_torch import CIFAR10Dataset
from templates.modules.models.tiny_cnn_cifar import CIFAR10SimpleCNN


class CIFAR10Strategy(TorchStrategyBase):
    '''
    Class for CIFAR-10 using CNN and FedAvg
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, is_local, device, base64_state)

        self.dataset = CIFAR10Dataset(dataset_params)

        if base64_state is None:
            # init the global model
            self.global_model = CIFAR10SimpleCNN()

            self.local_model = CIFAR10SimpleCNN()
            # self.prev_local_model = CIFAR10SimpleCNN()

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''
        # move local model to previous local model
        # self.prev_local_model = self.local_model

        # set the parameters for local as global model
        self.local_model.load_state_dict(self.global_model.state_dict())

    def train(self) -> None:
        '''
        Executes CrossEntropyLoss and Adam based Loop
        '''

        # move the local_model to the device, cpu or gpu
        self.local_model = self.local_model.to(self.device)

        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(
            self.local_model.parameters(), lr=self.learning_rate)

        # Epoch loop
        for epoch in range(self.train_epochs):
            self.local_model.train()
            total_loss = 0.0

            for i, (inputs, labels) in enumerate(self._train_set, 1):

                # move tensors to the device, cpu or gpu
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.local_model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

                print(
                    f'Processing Batch {i}/{len(self._train_set)}.', end='\r')

            average_loss = total_loss / len(self._train_set)
            print(
                f"Epoch [{epoch + 1}/{self.train_epochs}] - Loss: {average_loss:.4f}")

    def test(self) -> dict:
        '''
        Tests the model using the test loader, and returns the metrics as a dict
        '''

        # move the model to the device, cpu or gpu and set to evaluation
        if self.is_local:
            model = self.local_model.to(self.device)
        else:
            model = self.global_model.to(self.device)

        model.eval()

        # the actual labels and predictions lists
        actuals = []
        preds = []

        criterion = torch.nn.CrossEntropyLoss()

        with torch.no_grad():

            val_loss = 0.0

            for i, (inputs, labels) in enumerate(self._test_set, 1):
                # move tensors to the device, cpu or gpu
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                outputs = model(inputs)

                loss = criterion(outputs, labels)
                val_loss += loss.item()

                _, predicted = torch.max(outputs.data, 1)
                # val_total += labels.size(0)
                # val_correct += (predicted == labels).sum().item()

                actuals += labels.tolist()
                preds += predicted.tolist()

                print(
                    f'Processing batch {i} out of {len(self._test_set)}', end='\r')

            average_loss = val_loss / len(self._test_set)

        results = self.__get_metrics(actuals, preds)

        results['loss'] = average_loss if not math.isnan(
            average_loss) else -420.0

        print(
            f"Model Test Report:\n{results['classification_report']}\nLoss: {results['loss']}")

        return results

    def aggregate(self):
        '''
        Implementaion of the FedAvg Aggregation Algorithm for this strategy.
        '''
        super()._pre_aggregation()

        with torch.no_grad():
            self.global_model = self.global_model.to(self.device)

            # get the model parameters
            global_params = self.global_model.state_dict()

            # Initialize global parameters to zeros
            for param_name, param in global_params.items():
                param.zero_()

            # Aggregate client updates
            for client_obj, weight in zip(self.client_objects, self.client_weights):
                client_obj.local_model = client_obj.local_model.to(self.device)
                client_state_dict = client_obj.local_model.state_dict()

                for param_name, param in client_state_dict.items():
                    global_params[param_name] += (weight * param).type(
                        global_params[param_name].dtype)

            self.global_model.load_state_dict(global_params)

        super()._post_aggregation()

    def append_client_object(self, bash64_state: str, client_weight: float) -> None:
        '''
        Append client objects from their base64 state strings
        '''

        self.client_objects.append(CIFAR10Strategy(
            {}, True, self.device, bash64_state))

        self.client_weights.append(client_weight)

    @staticmethod
    def __get_metrics(actuals: list, preds: list) -> dict:
        '''
        Returns a dictionary of evaluation metrics.
        accuracy, precision, recall, f-1 score, f-1 macro, f-1 micro, confusion matrix
        '''

        # print(actuals, preds)

        accuracy = metrics.accuracy_score(actuals, preds)
        precision_weighted = metrics.precision_score(actuals, preds,
                                                     average='weighted')
        precision_macro = metrics.precision_score(actuals, preds,
                                                  average='macro')
        recall_weighted = metrics.recall_score(
            actuals, preds, average='weighted')
        recall_macro = metrics.recall_score(actuals, preds, average='macro')
        f1_macro = metrics.f1_score(actuals, preds, average='macro')
        f1_weighted = metrics.f1_score(actuals, preds, average='weighted')
        confusion_matrix = metrics.confusion_matrix(actuals, preds).tolist()
        report = metrics.classification_report(actuals, preds)

        results = {
            'accuracy': accuracy,
            'precision_weighted': precision_weighted,
            'precision_macro': precision_macro,
            'recall_weighted': recall_weighted,
            'recall_macro': recall_macro,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
            'confusion_matrix': confusion_matrix,
            'classification_report': report
        }

        return results


# Dont forget to set this the alias as 'StrategyDefinition'
StrategyDefinition = CIFAR10Strategy
