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

    (data, labels) = dataset

    # get the unique labels
    classes = torch.unique(labels)

    # sort and segregate the labels sequentially
    data_class_chunks = []
    labels_class_chunks = []
    for y_ in classes:
        idx = torch.stack([y_ == labels]).sum(
            0).bool()  # get indices for the class
        data_class_chunks.append(data[idx])
        labels_class_chunks.append(labels[idx])

    data = torch.cat(data_class_chunks, 0)
    labels = torch.cat(labels_class_chunks, 0)

    # count the total samples
    total_data_samples = len(data)

    # calculate the split sections
    split_sections = [int(total_data_samples*weight)
                      for weight in client_weights]

    # split the data and labels into chunks
    data_chunks = torch.split(data, split_size_or_sections=split_sections)
    label_chunks = torch.split(labels, split_size_or_sections=split_sections)

    # create dataset tuples for client chunks
    client_chunks = []
    for i in range(len(client_weights)):
        # shuffle the samples using the permutation
        idx = torch.randperm(len(label_chunks[i]))

        # shuffle and add to the tuple
        client_chunk = (data_chunks[i][idx], label_chunks[i][idx])

        client_chunks.append(client_chunk)

    return client_chunks, client_weights
