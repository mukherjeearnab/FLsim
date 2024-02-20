'''
DistLearn Strategy for training CIFAR-10 on a simple CNN,
using FedAvg Aggregation
'''
from time import sleep
import numpy as np
from sklearn import metrics
from sklearn.preprocessing import LabelBinarizer
from templates.strategy.base.sklearn_strategy import SKLearnStrategyBase
from templates.dataset.cifar10_tensorflow import CIFAR10Dataset
from sklearn.neural_network import MLPClassifier


class SKLearnMNIST(SKLearnStrategyBase):
    '''
    Class for CIFAR-10 using CNN and FedAvg
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, dataset_params, is_local, device, base64_state)

        self.dataset = CIFAR10Dataset(dataset_params)

        self._n_classes = 10  # MNIST has 10 classes
        self._n_features = 784  # Number of features in dataset

        if base64_state is None:
            # init the global model
            self.global_model = MLPClassifier(hidden_layer_sizes=(100,), alpha=1e-4,
                                              solver='adam', verbose=10, tol=1e-4, random_state=1,
                                              learning_rate_init=.001,
                                              early_stopping=False,
                                              max_iter=1,  # ,  # local epoch
                                              warm_start=True  # prevent refreshing weights when fitting
                                              )

            self.local_model = MLPClassifier(hidden_layer_sizes=(100,), alpha=1e-4,
                                             solver='adam', verbose=10, tol=1e-4, random_state=1,
                                             learning_rate_init=.001,
                                             early_stopping=False,
                                             max_iter=1,  # ,  # local epoch
                                             warm_start=True  # prevent refreshing weights when fitting
                                             )

            # self.global_model.n_layers_ = 3
            # self.local_model.n_layers_ = 3

            # self.global_model.out_activation_ = 'softmax'
            # self.local_model.out_activation_ = 'softmax'

            # self.global_model.n_outputs_ = self._n_classes
            # self.local_model.n_outputs_ = self._n_classes

            # self.global_model.coefs_ = [
            #     np.zeros((3072, 100)),
            #     np.zeros((100, self._n_classes))
            # ]
            # self.local_model.coefs_ = [
            #     np.zeros((3072, 100)),
            #     np.zeros((100, self._n_classes))
            # ]

            # self.global_model.intercepts_ = [
            #     np.zeros((100,)),
            #     np.zeros((self._n_classes,))
            # ]
            # self.local_model.intercepts_ = [
            #     np.zeros((100,)),
            #     np.zeros((self._n_classes,))
            # ]

            # self.global_model.classes_ = np.array(
            #     [i for i in range(self._n_classes)])
            # self.local_model.classes_ = np.array(
            #     [i for i in range(self._n_classes)])

            lb = LabelBinarizer()
            lb.fit([i for i in range(self._n_classes)])
            fake_data, fake_labels = np.zeros(
                (self._n_classes, 3072)), np.array([i for i in range(self._n_classes)])

            self.local_model.fit(
                fake_data, fake_labels)
            self.global_model.fit(
                fake_data, fake_labels)

    def load_dataset(self, train_set, test_set):
        super().load_dataset(train_set, test_set)

        # lb = LabelBinarizer()
        # lb.fit([i for i in range(self._n_classes)])

        if self.is_local:
            self._train_set = list(train_set)
            self._train_set[0] = self._train_set[0].reshape(
                self._train_set[0].shape[0], -1)
            # self._train_set[1] = lb.transform(self._train_set[1])
            self._train_set = tuple(self._train_set)

        self._test_set = list(test_set)
        self._test_set[0] = self._test_set[0].reshape(
            self._test_set[0].shape[0], -1)
        # self._test_set[1] = lb.transform(self._test_set[1])
        self._test_set = tuple(self._test_set)

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''
        # move local model to previous local model
        # self.prev_local_model = self.local_model

        # set the parameters for local as global model
        self.local_model.coefs_ = self.global_model.coefs_
        # self.local_model.intercepts_ = self.global_model.intercepts_

    def train(self) -> None:
        '''
        Executes Fit for the model
        '''

        data, labels = self._train_set

        # Epoch loop
        for epoch in range(self.train_epochs):
            self.local_model.partial_fit(
                data, labels, classes=self.local_model.classes_)

            print(f"Epoch [{epoch + 1}/{self.train_epochs}]")

        print(self.local_model.n_layers_)
        for coef in self.local_model.intercepts_:
            print(coef.shape)
        print(self.local_model)

    def test(self) -> dict:
        '''
        Tests the model using the test loader, and returns the metrics as a dict
        '''

        data, labels = self._test_set

        # move the model to the device, cpu or gpu and set to evaluation
        if self.is_local:
            model = self.local_model
        else:
            model = self.global_model

        preds = model.predict(data)

        # preds = np.argmax(preds, axis=1)
        # labels = np.argmax(labels, axis=1)

        # loss = metrics.log_loss(labels, model.predict_proba(data))

        results = self.__get_metrics(labels, preds)

        # results['loss'] = loss

        print(
            f"Model Test Report:\n{results['classification_report']}")

        return results

    def aggregate(self):
        '''
        Implementaion of the FedAvg Aggregation Algorithm for this strategy.
        '''
        super()._pre_aggregation()

        sleep(2)

        # Aggregate client updates
        for i, _ in enumerate(self.global_model.coefs_):
            self.global_model.coefs_[i] = self.client_weights[0] * \
                self.client_objects[0].local_model.coefs_[i]

        # for i, _ in enumerate(self.global_model.intercepts_):
        #     self.global_model.intercepts_[i] = self.client_weights[0] * \
        #         self.client_objects[0].local_model.intercepts_[i]

        for client_obj, weight in zip(self.client_objects[1:], self.client_weights[1:]):
            for i, _ in enumerate(self.global_model.coefs_):
                self.global_model.coefs_[i] += weight * \
                    client_obj.local_model.coefs_[i]

            # for i, _ in enumerate(self.global_model.intercepts_):
            #     self.global_model.intercepts_[i] += weight * \
            #         client_obj.local_model.intercepts_[i]

        super()._post_aggregation()

    def append_client_object(self, bash64_state: str, client_weight: float) -> None:
        '''
        Append client objects from their base64 state strings
        '''

        self.client_objects.append(SKLearnMNIST(
            {}, {}, True, self.device, bash64_state))

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
StrategyDefinition = SKLearnMNIST
