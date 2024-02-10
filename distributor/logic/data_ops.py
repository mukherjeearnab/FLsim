'''
Modue Containing Functions to operate on torch dataset
'''
import dill
import base64
from base.dataset_base import DatasetBase


def init_dataset_object(definition: str, dist_params: dict) -> DatasetBase:
    '''
    Create the dataset object and return it
    '''

    DatasetClass = dill.loads(base64.b64decode(definition.encode()))
    dataset_obj = DatasetClass(dist_params)

    return dataset_obj


def train_test_split(train_set, dataset: DatasetBase) -> tuple:
    '''
    Creates train and test sets by splitting the original training set
    '''

    return dataset.train_test_split_method(train_set)


def create_central_testset(dataset_obj: DatasetBase, client_test_sets: list) -> tuple:
    '''
    Appendd all the client test sets into a single test set, 
    which will be used by the server to test the global model.
    '''
    # create a list of all the data and labels for each client
    data = [t[0] for t in client_test_sets]
    labels = [t[1] for t in client_test_sets]

    # concatenate the data and labels into a single tensor
    data = dataset_obj.concatenate_method(data)
    labels = dataset_obj.concatenate_method(labels)

    return (data, labels)
