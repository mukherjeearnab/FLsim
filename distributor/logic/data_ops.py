'''
Modue Containing Functions to operate on torch dataset
'''
import torch
import numpy


def train_test_split(dataset: tuple, split_weights: list) -> tuple:
    '''
    Creates train and test sets by splitting the original dataset into 
    len(split_weights) chunks.
    '''

    data, labels = dataset

    total_data_samples = len(data)

    # calculate the split sections
    split_sections = [int(total_data_samples*weight)
                      for weight in split_weights]

    if sum(split_sections) < total_data_samples:
        split_sections[-1] += total_data_samples - sum(split_sections)
    else:
        split_sections[0] -= sum(split_sections) - total_data_samples

    # split the data and labels into chunks
    data_chunks = torch.split(data, split_size_or_sections=split_sections)
    label_chunks = torch.split(labels, split_size_or_sections=split_sections)

    # create dataset tuples for client chunks
    train_test_chunks = []
    for i in range(len(split_weights)):
        split_chunk = (data_chunks[i], label_chunks[i])

        train_test_chunks.append(split_chunk)

    # returns (train_set, test_set)
    return (train_test_chunks[0], train_test_chunks[1])


def create_central_testset(client_test_sets: list) -> tuple:
    '''
    Appendd all the client test sets into a single test set, 
    which will be used by the server to test the global model.
    '''
    # create a list of all the data and labels for each client
    data = [t[0] for t in client_test_sets]
    labels = [t[1] for t in client_test_sets]

    # concatenate the data and labels into a single tensor
    if isinstance(data[0], numpy.ndarray):
        # if numpy ndarray
        data = numpy.concatenate(data, 0)
        labels = numpy.concatenate(labels, 0)
    else:
        # if pytorch tensor
        data = torch.cat(data, 0)
        labels = torch.cat(labels, 0)

    return (data, labels)
