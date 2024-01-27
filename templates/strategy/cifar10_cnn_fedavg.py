'''
DistLearn Strategy for training CIFAR-10 on a simple CNN,
using FedAvg Aggregation
'''
import math
from copy import deepcopy
import torch
from sklearn import metrics
from templates.strategy.base.learn_strategy import LearnStrategyBase
from templates.models.simple_cnn_cifar import ModelClass as SimpleCNN


class CIFAR10Strategy(LearnStrategyBase):
    '''
    Class for CIFAR-10 using CNN and FedAvg
    '''

    def __init__(self, hyperparams: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, is_local, device, base64_state)

        # init the global model
        self.global_model = SimpleCNN()

        # if instance is local client instance,
        # then set the local models
        if self.is_local:
            self.local_model = SimpleCNN()
            self.prev_local_model = SimpleCNN()

            raise NotImplementedError

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''
        # move local model to previous local model
        self.prev_local_model = self.local_model

        # set the parameters for local as global model
        self.local_model.load_state_dict(self.global_model.state_dict())

    def train(self, train_loader: torch.utils.data.DataLoader) -> None:
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

            for i, (inputs, labels) in enumerate(train_loader, 1):

                # move tensors to the device, cpu or gpu
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.local_model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

                print(f'Processing Batch {i}/{len(train_loader)}.', end='\r')

            average_loss = total_loss / len(train_loader)
            print(
                f"Epoch [{epoch + 1}/{self.train_epochs}] - Loss: {average_loss:.4f}")

    def test(self, test_loader: torch.utils.data.DataLoader) -> dict:
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

            for i, (inputs, labels) in enumerate(test_loader, 1):
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
                    f'Processing batch {i} out of {len(test_loader)}', end='\r')

            average_loss = val_loss / len(test_loader)

        results = self.__get_metrics(actuals, preds)

        results['loss'] = average_loss if not math.isnan(
            average_loss) else -420.0

        return results

    def aggregate(self):
        '''
        Implementaion of the FedAvg Aggregation Algorithm for this strategy.
        '''

        with torch.no_grad():
            # get the model parameters
            global_params = self.global_model.state_dict()

            new_global_params = deepcopy(global_params)  # Create a deep copy

            # Initialize global parameters to zeros
            for param_name, param in new_global_params.items():
                param = param.to(self.device)
                param.zero_()

            # Aggregate client updates
            for client_obj, weight in zip(self.client_objects, self.client_weights):
                client_state_dict = client_obj.local_model.state_dict()
                for param_name, param in client_state_dict.items():
                    # move client param to gpu
                    param = param.to(self.device)

                    new_global_params[param_name] += (weight * param).type(
                        new_global_params[param_name].dtype)

            self.global_model.load_state_dict(new_global_params)

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
