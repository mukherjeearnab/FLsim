'''
The Training Processes Module
'''
from helpers.file import torch_read
from helpers.dynamod import load_module
from helpers.logging import logger


def data_preprocessing(file_name: str, dataset_path: str, preprocessing_module_str: str) -> tuple:
    '''
    Dataset Preprocessing Method.
    Takes input as the raw dataset path, and the preprocessing module as string.
    Loads the preprocessing module and processes the dataset after loading it from disk.
    '''

    # load the dataset and preprocessing module
    dataset = torch_read(file_name, dataset_path)
    preprocessor_module = load_module('preprocessor', preprocessing_module_str)

    # obtain the train and test sets
    (train, test) = dataset

    # preprocess train and test datasets
    (train_processed, test_processed) = preprocessor_module.preprocess_dataset(train, test)

    return (train_processed, test_processed)
