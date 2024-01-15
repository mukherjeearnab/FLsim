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


def init_model(model_module_str: str):
    '''
    Initializes the model and returns it
    '''

    # load the model module
    model_module = load_module('model_module', model_module_str)

    # create an instance of the model
    model = model_module.ModelClass()

    return model


def parameter_mixing(current_global_params: dict, previous_local_params: dict, mixer_module: str) -> dict:
    '''
    Loads the parameter mixer and updates the parameters and returns it.
    '''

    # load the model module
    mixer_module = load_module('model_module', mixer_module)

    # create an instance of the model
    params = mixer_module.param_mixer(
        current_global_params, previous_local_params)

    return params


def train_model(job_manifest: dict, train_loader, local_model, global_model, prev_local_model, extra_data: dict, device) -> dict:
    '''
    Execute the Training Loop
    '''

    # load the train loop module
    train_loop_module = load_module('train_loop_module',
                                    job_manifest['client_params']['model_params']['training_loop_file']['content'])

    # assemble the hyperparameters
    num_epochs = job_manifest['client_params']['train_params']['local_epochs']
    learning_rate = job_manifest['client_params']['train_params']['learning_rate']
    extra_params = job_manifest['client_params']['train_params']['extra_params']

    logger.info(f'Starting Local Training with {num_epochs} EPOCHS')

    # train the model
    train_loop_module.train_loop(num_epochs, learning_rate, train_loader,
                                 local_model, global_model, prev_local_model,
                                 extra_params, extra_data, device)

    logger.info(f'Completed Local Training with {num_epochs} EPOCHS')
