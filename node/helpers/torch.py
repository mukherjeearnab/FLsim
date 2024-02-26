'''
Torch specific functionality module
'''
import os
import random
import torch
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv


load_dotenv()
USE_CUDA = int(os.getenv('USE_CUDA'))
DETERMINISTIC = int(os.getenv('DETERMINISTIC'))
RANDOM_SEED = int(os.getenv('RANDOM_SEED'))

if DETERMINISTIC == 1:
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"

    # set torch deterministic properties
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)

    # set seed on startup
    tf.random.set_seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)
    torch.cuda.manual_seed_all(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)


# set tensorflow logger
tf.get_logger().setLevel('ERROR')


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
    if DETERMINISTIC == 1:
        # set seed on startup
        tf.random.set_seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        torch.cuda.manual_seed_all(RANDOM_SEED)
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)
