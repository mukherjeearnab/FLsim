'''
Torch specific functionality module
'''
import os
import random
import torch
import numpy as np
from dotenv import load_dotenv

# set seed on startup
torch.manual_seed(0)
random.seed(0)
np.random.seed(0)

load_dotenv()
USE_CUDA = int(os.getenv('USE_CUDA'))


def get_device():
    '''
    Gets the device, gpu, if available else cpu
    '''

    if torch.cuda.is_available() and USE_CUDA == 1:
        dev = "cuda:0"
    else:
        dev = "cpu"
    device = torch.device(dev)

    return device


def reset_seed():
    '''
    Reset the Manual Seed for Deterministic Execution
    '''
    torch.manual_seed(0)
    random.seed(0)
    np.random.seed(0)
