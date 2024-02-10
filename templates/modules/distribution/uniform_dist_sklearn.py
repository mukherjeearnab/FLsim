'''
Creates a uniform distribution of dataset of k clients.
returns as a list of np arrays
'''
import numpy as np


def distribute_into_client_chunks(dataset: tuple, client_weights: list, extra_params: dict, train=False) -> list:
    '''
    Creates client chunks by splitting the original dataset into 
    len(client_weights) chunks, based on the diritchlet distribution.
    '''
    _ = extra_params

    data, labels = dataset

    # create the client data and label chunks
    data_chunks = np.array_split(data, len(client_weights))
    label_chunks = np.array_split(labels, len(client_weights))

    # create dataset tuples for client chunks
    client_chunks = []
    for i in range(len(client_weights)):
        client_chunk = (data_chunks[i], label_chunks[i])

        client_chunks.append(client_chunk)

    # create new client weights
    new_client_weights = [len(label_chunk) for label_chunk in label_chunks]
    new_client_weights = [float(total)/sum(new_client_weights)
                          for total in new_client_weights]

    return client_chunks, new_client_weights
