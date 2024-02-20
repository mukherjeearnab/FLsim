'''
DistLearn Strategy for Tensorflow Workflow
'''
from copy import deepcopy
import tensorflow as tf
import numpy as np
from sklearn import metrics
from templates.strategy.base.learn_strategy import LearnStrategyBase
from templates.dataset.cifar10_tensorflow import CIFAR10Dataset


class CIFAR10StrategyTF(LearnStrategyBase):
    '''
    Class for Strategy Base for Tensorflow-based training
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        super().__init__(hyperparams, dataset_params, is_local, device, base64_state)

        self.dataset = CIFAR10Dataset(dataset_params)

        tf.config.set_visible_devices([], 'GPU')
        # tf.keras.initializers.RandomUniform(
        #     minval=-0.05, maxval=0.05, seed=10)
        # physical_devices = tf.config.list_physical_devices('CPU')
        # tf.config.experimental.set_memory_growth(physical_devices[0], True)

        if base64_state is None:
            # init the global model
            self.global_model = self.load_model()

            self.local_model = self.load_model()

    # def load_dataset(self, train_set, test_set):
    #     '''
    #     Load the training and testing datasets
    #     '''
    #     super().load_dataset(train_set, test_set)

    #     # if self._train_set is not None:
    #     #     self._train_set = list(self._train_set)

    #     #     # self._train_set[0] = np.transpose(self._train_set[0], (0, 3, 2, 1))
    #     #     self._train_set[1] = tf.one_hot(
    #     #         self._train_set[1].astype(np.int32), depth=10)

    #     #     self._train_set = tuple(self._train_set)

    #     # self._test_set = list(self._test_set)

    #     # # self._test_set[0] = np.transpose(self._test_set[0], (0, 3, 2, 1))
    #     # self._test_set[1] = tf.one_hot(
    #     #     self._test_set[1].astype(np.int32), depth=10)

    #     # self._test_set = tuple(self._test_set)

    #     # print(self._test_set[0].shape)

    def parameter_mixing(self) -> None:
        '''
        An empty parameter mixing,
        Basically load the global parameters to the local model
        '''

        self.local_model.set_weights(self.global_model.get_weights())

    def train(self) -> None:
        '''
        Executes CrossEntropyLoss and Adam based Loop
        '''

        _ = self.local_model.fit(self._train_set[0], self._train_set[1],
                                 batch_size=self.train_batch_size, epochs=self.train_epochs)

    def test(self) -> dict:
        '''
        Tests the model using the test loader, and returns the metrics as a dict
        '''

        if self.is_local:
            model = self.local_model
        else:
            model = self.global_model

        loss, _ = model.evaluate(
            self._test_set[0], self._test_set[1])

        preds = model.predict(self._test_set[0])
        actuals = self._test_set[1]

        # print(preds, actuals)

        preds = np.argmax(preds, axis=1)
        # actuals = np.argmax(actuals, axis=0)

        results = self.__get_metrics(actuals, preds)
        results['loss'] = loss

        print(
            f"Model Test Report:\n{results['classification_report']}\nLoss: {results['loss']}")

        return results

    def aggregate(self):
        '''
        Implementaion of the FedAvg Aggregation Algorithm for this strategy.
        '''

        super()._pre_aggregation()

        averaged_layers = []

        # Iterate over each layer of the global model
        for layer_idx, layer in enumerate(self.global_model.layers):
            global_layer_weights = deepcopy(layer.get_weights())
            reference_layer_weights = deepcopy(layer.get_weights())

            # Iterate over each client model
            for client_obj, weight in zip(self.client_objects, self.client_weights):
                local_model = client_obj.local_model
                # Retrieve the weights of the corresponding layer in the client model
                client_layer_weights = local_model.layers[layer_idx].get_weights(
                )

                print(len(reference_layer_weights), len(client_layer_weights))

                for i, (w_g, w_l) in enumerate(zip(reference_layer_weights, client_layer_weights)):
                    grad = w_l - w_g
                    weighted_grad = grad * weight

                    global_layer_weights[i] += weighted_grad

            self.global_model.layers[layer_idx].set_weights(
                global_layer_weights)

            # averaged_layers.append(global_layer_weights)

        # print(len(averaged_layers), len(self.global_model.layers))
        # exit()

        # Update global model with averaged weights
        # self.global_model.set_weights(averaged_layers)

        super()._post_aggregation()

    def append_client_object(self, bash64_state: str, client_weight: float) -> None:
        '''
        Append client objects from their base64 state strings
        '''

        self.client_objects.append(CIFAR10StrategyTF(
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

    def load_model(self):
        '''
        Load the Tensorflow Sequential Model
        '''

        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Conv2D(
            32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Conv2D(
            64, (3, 3), activation='relu'))
        model.add(tf.keras.layers.MaxPooling2D((2, 2)))
        model.add(tf.keras.layers.Conv2D(
            64, (3, 3), activation='relu'))
        model.add(tf.keras.layers.Flatten())
        model.add(tf.keras.layers.Dense(64, activation='relu'))
        model.add(tf.keras.layers.Dense(10))

        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=['acc'])

        return model


# Dont forget to set this the alias as 'StrategyDefinition'
StrategyDefinition = CIFAR10StrategyTF
