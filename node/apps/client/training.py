'''
The Training Processes Module
'''
from base.learn_strategy import LearnStrategyBase
from helpers.file import torch_read


def data_preprocessing(file_name: str, dataset_path: str, strategy: LearnStrategyBase) -> tuple:
    '''
    Dataset Preprocessing Method.
    Takes input as the raw dataset path, and the preprocessing module as string.
    Loads the preprocessing module and processes the dataset after loading it from disk.
    '''

    # load the dataset and preprocessing module
    dataset = torch_read(file_name, dataset_path)

    # obtain the train and test sets
    (train, test) = dataset

    # preprocess train and test datasets
    (train_processed, test_processed) = strategy.dataset.preprocess_data(train, test)

    return (train_processed, test_processed)
