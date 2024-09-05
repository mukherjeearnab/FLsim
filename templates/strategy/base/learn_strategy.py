'''
Base learning strategy module
'''
import io
import base64
from typing import Any
from copy import deepcopy
import torch
from templates.dataset.base.dataset_base import DatasetBase


class LearnStrategyBase(object):
    '''
    Base class for learning strategies for DistLearn Framework
    '''

    def __init__(self, hyperparams: dict, dataset_params: dict, is_local: bool, device='cpu', base64_state=None):
        # model attributes
        self.global_model = None
        self.local_model = None
        self.prev_local_model = None

        # client objects
        self.client_objects = list()
        self.client_weights = list()

        # client and worker learning hyper-parameters
        self.learning_rate = hyperparams['learning_rate'] if 'learning_rate' in hyperparams else None
        self.train_batch_size = hyperparams['train_batch_size'] if 'train_batch_size' in hyperparams else None
        self.test_batch_size = hyperparams['test_batch_size'] if 'test_batch_size' in hyperparams else None
        self.train_epochs = hyperparams['train_epochs'] if 'train_epochs' in hyperparams else None
        self.client_extra_params = hyperparams['client_extra_params'] if 'client_extra_params' in hyperparams else None
        self.worker_extra_params = hyperparams['worker_extra_params'] if 'worker_extra_params' in hyperparams else None

        # dataset_object =
        self.dataset = DatasetBase(dataset_params)
        self._train_set = None
        self._test_set = None

        # extra states
        self.is_local = is_local
        self.device = device

        if base64_state is not None:
            self.load_base64_state(base64_state)

    def load_dataset(self, train_set, test_set):
        '''
        Load the training and testing datasets
        '''

        if self.is_local:
            self._train_set = train_set

        self._test_set = test_set

    def parameter_mixing(self):
        '''
        Method to mix parameters from global and previous local parameters
        This also sets the local parameter as the new global parameter
        '''

        raise NotImplementedError

    def train(self):
        '''
        Method to train the model for e epochs
        '''

        raise NotImplementedError

    def test(self):
        '''
        Method to test the model
        '''

        raise NotImplementedError

    def aggregate(self):
        '''
        Method to execute Federated Aggregation 
        '''

        raise NotImplementedError

    def append_client_object(self, bash64_state: Any, client_weight: float) -> None:
        '''
        Append client objects from their base64 state strings
        '''

        raise NotImplementedError

    def get_local_payload(self):
        '''
        Method to get the local client payload for export
        '''

        with torch.no_grad():
            payload = dict()
            for key, value in self.__dict__.items():
                # remove private and protected fields
                if not key.startswith('_'):
                    payload[key] = deepcopy(value)

        # delete the unnecessary fields
        del payload['global_model']
        del payload['prev_local_model']

        del payload['client_objects']
        del payload['client_weights']

        del payload['learning_rate']
        del payload['train_batch_size']
        del payload['test_batch_size']
        del payload['train_epochs']
        del payload['client_extra_params']
        del payload['worker_extra_params']

        del payload['is_local']
        del payload['device']

        return payload

    def get_global_payload(self):
        '''
        Method to get the global worker payload for export
        '''

        with torch.no_grad():
            payload = dict()
            for key, value in self.__dict__.items():
                # remove private and protected fields
                if not key.startswith('_'):
                    payload[key] = deepcopy(value)

        # delete the unnecessary fields
        del payload['local_model']
        del payload['prev_local_model']

        del payload['client_objects']
        del payload['client_weights']

        del payload['learning_rate']
        del payload['train_batch_size']
        del payload['test_batch_size']
        del payload['train_epochs']
        del payload['client_extra_params']
        del payload['worker_extra_params']

        del payload['is_local']
        del payload['device']

        return payload

    def get_base64_local_payload(self):
        '''
        Get Base 64 encoded local payload for export
        '''

        payload = self.get_local_payload()

        b64_payload = self.__base64_encode(payload)

        return b64_payload

    def get_base64_global_payload(self):
        '''
        Get Base 64 encoded global payload for export
        '''

        payload = self.get_global_payload()

        b64_payload = self.__base64_encode(payload)

        return b64_payload

    def load_base64_state(self, base64_state: str):
        '''
        Load the Object state from the base64 string of pickled __dict__
        '''

        state_dict = self.__base64_decode(base64_state)

        for key, value in state_dict.items():
            self.__dict__[key] = value

    def _pre_aggregation(self):
        '''
        Pre-aggregation Checks and Actions
        '''

        for client_obj in self.client_objects:
            if client_obj.local_model is None:
                client_obj.local_model = client_obj.global_model

    def _post_aggregation(self):
        '''
        Post-aggregation Checks and Actions
        '''

        # empty out client_objects
        self.client_objects = list()
        self.client_weights = list()

    # @staticmethod
    def __base64_encode(self, obj: Any) -> str:
        '''
        Static function to Base 64 encode an object using torch.save pickling
        '''

        # create a bytes stream
        buff = io.BytesIO()

        # save the state dict into the stream
        torch.save(obj, buff)

        # move the stream seek to intial position
        buff.seek(0)

        # convert into a string of base64 representation form thte bytes stream
        b64_payload = base64.b64encode(buff.read()).decode("utf8")

        return b64_payload

    # @staticmethod
    def __base64_decode(self, base64str: str) -> Any:
        '''
        Static function to decode a Base 64 string to object using torch.load unpickling
        '''
        # encode the string into base64
        obj_data = base64str.encode()
        # apply base64 decode to obtain bytes
        obj_bytes = base64.b64decode(obj_data)

        # converts into bytes stream and load using torch.load
        obj = torch.load(io.BytesIO(obj_bytes),
                         map_location=self.device)

        return obj
