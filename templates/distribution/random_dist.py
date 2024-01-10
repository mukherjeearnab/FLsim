'''
Creates a random distribution of dataset of k clients.
returns as a list of tensors
'''
import torch


def distribute_into_client_chunks(dataset: tuple, client_weights: list, extra_params: dict, train=False) -> list:
    '''
    Creates random chunks by splitting the original dataset into 
    len(client_weights) chunks, based on the client weights.
    '''

    _ = extra_params
    data, labels = dataset

    total_data_samples = len(data)

    # calculate the split sections
    split_sections = [int(total_data_samples*weight)
                      for weight in client_weights]

    split_sections[-1] = total_data_samples - sum(split_sections[:-1])

    # split the data and labels into chunks
    data_chunks = torch.split(data, split_size_or_sections=split_sections)
    label_chunks = torch.split(labels, split_size_or_sections=split_sections)

    # create dataset tuples for client chunks
    client_chunks = []
    for i in range(len(client_weights)):
        client_chunk = (data_chunks[i], label_chunks[i])

        client_chunks.append(client_chunk)

    return client_chunks, client_weights
