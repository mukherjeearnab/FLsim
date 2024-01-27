'''
Base learning strategy module
'''
import io
import base64
from typing import Any
from copy import deepcopy
import torch


class LearnStrategyBase(object):
    '''
    Base class for learning strategies for DistLearn Framework
    '''

    def __init__(self, hyperparams: dict, is_local: bool, device='cpu', base64_state=None):
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

        # extra states
        self.is_local = is_local
        self.device = device

        if base64_state is not None:
            self.load_base64_state(base64_state)

    def parameter_mixing(self):
        '''
        Method to mix parameters from global and previous local parameters
        This also sets the local parameter as the new global parameter
        '''

        raise NotImplementedError

    def train(self, train_loader: torch.utils.data.DataLoader):
        '''
        Method to train the model for e epochs
        '''

        _ = train_loader

        raise NotImplementedError

    def test(self, test_loader: torch.utils.data.DataLoader):
        '''
        Method to test the model
        '''

        _ = test_loader

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
            payload = deepcopy(self.__dict__)

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

        # remove private and protected fields
        for key in payload.keys():
            if key.startswith('_'):
                del payload[key]

        return payload

    def get_global_payload(self):
        '''
        Method to get the global worker payload for export
        '''

        with torch.no_grad():
            payload = deepcopy(self.__dict__)

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

        # remove private and protected fields
        for key in payload.keys():
            if key.startswith('_'):
                del payload[key]

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

    @staticmethod
    def __base64_encode(obj: Any) -> str:
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

    @staticmethod
    def __base64_decode(base64str: str) -> Any:
        '''
        Static function to decode a Base 64 string to object using torch.load unpickling
        '''

        # encode the string into base64
        obj_data = base64str.encode()

        # apply base64 decode to obtain bytes
        obj_bytes = base64.b64decode(obj_data)

        # converts into bytes stream and load using torch.load
        obj = torch.load(io.BytesIO(obj_bytes))

        return obj
