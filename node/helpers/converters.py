'''
A Module with functions to handle and convert Tensors into floats and overall model management
'''
import io
import base64
from collections import OrderedDict
import torch
import torch.utils.data as data_utils


def set_state_dict(model, state_dict: dict) -> None:
    '''
    Set the State Dict of a model as a Dictionart of List of Floats
    '''
    tensor_state_dict = convert_list_to_tensor(state_dict)
    model.load_state_dict(tensor_state_dict)


def get_state_dict(model) -> dict:
    '''
    Get the State Dict of a model as a Dictionart of List of Floats
    '''
    tensor_state_dict = model.state_dict()
    state_dict = convert_tensor_to_list(tensor_state_dict)
    return state_dict


def set_base64_state_dict(model, base64_state_dict: str) -> None:
    '''
    Set the Base64 Representation of a state dict to the model 
    '''

    state_dict = convert_base64_to_state_dict(base64_state_dict)

    model.load_state_dict(state_dict)


def get_base64_state_dict(model) -> str:
    '''
    Get the State Dict of a model as a Base64 String
    '''

    b64_state_dict = convert_state_dict_to_base64(model.state_dict())

    return b64_state_dict


def convert_base64_to_state_dict(base64_params: str, device='cpu'):
    '''
    Convert a base64 state dict string into a pytorch state dict object
    '''

    # encode the string into base64
    dict_data = base64_params.encode()

    # apply base64 decode to obtain bytes
    dict_bytes = base64.b64decode(dict_data)

    # converts into bytes stream and load using torch.load
    state_dict = torch.load(io.BytesIO(dict_bytes))

    for key in state_dict.keys():
        state_dict[key] = state_dict[key].to(device)

    return state_dict


def convert_state_dict_to_base64(state_dict: OrderedDict) -> str:
    '''
    Convert a PyTorch Model State Dict into it's base64 representation
    '''

    # create a bytes stream
    buff = io.BytesIO()

    # save the state dict into the stream
    torch.save(state_dict, buff)

    # move the stream seek to intial position
    buff.seek(0)

    # convert into a string of base64 representation form thte bytes stream
    b64_state_dict = base64.b64encode(buff.read()).decode("utf8")

    return b64_state_dict


def convert_list_to_tensor(params: OrderedDict, device='cpu') -> dict:
    '''
    Converts an OrderedDict of Tensors into a Dictionary of Lists of floats
    '''
    params_ = {}
    for key in params.keys():
        params_[key] = torch.tensor(params[key],
                                    dtype=torch.float32, device=device)

    return params_


# Convert State Dict Tensors to List
def convert_tensor_to_list(params: dict) -> dict:
    '''
    Converts an Dictionary of List of floats into a Dictionary of Tensors
    '''
    params_ = {}
    for key in params.keys():
        params_[key] = params[key].tolist()

    return params_


def tensor_to_data_loader(dataset: tuple, batch_size: int):
    '''
    convert dataset tensor to data loader object
    '''

    data, labels = dataset

    train = data_utils.TensorDataset(data, labels)
    train_loader = data_utils.DataLoader(
        train, batch_size, shuffle=True, num_workers=2)

    return train_loader
