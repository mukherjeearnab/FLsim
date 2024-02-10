'''
Creates a diritchlet distribution of dataset of k clients.
returns as a list of tensors
'''
import torch
import numpy as np
from collections import Counter


def distribute_into_client_chunks(dataset: tuple, client_weights: list, extra_params: dict, train=False) -> list:
    '''
    Creates client chunks by splitting the original dataset into 
    len(client_weights) chunks, based on the diritchlet distribution.
    '''
    alpha = extra_params['diritchlet']['alpha']
    seed = extra_params['diritchlet']['seed']

    # set np seed for reproducibility
    np.random.seed(seed)

    data, labels = dataset

    total_data_samples = len(data)

    # obtain the dataset indices
    indices = np.random.permutation(total_data_samples)

    # obtain non-iid client indices for client chunks
    client_idcs = split_noniid(
        indices, labels, alpha=alpha, n_clients=len(client_weights))

    # create the client data and label chunks
    data_chunks = [torch.index_select(data, 0, torch.LongTensor(
        idcs)) for idcs in client_idcs]
    label_chunks = [torch.index_select(labels, 0, torch.LongTensor(
        idcs)) for idcs in client_idcs]

    total_labels = 0
    for i, labels in enumerate(label_chunks):
        total_labels += len(labels)
        print(i, dict(Counter(labels.numpy())))
    print(total_labels)

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


def split_noniid(train_idcs, train_labels, alpha, n_clients):
    '''
    Splits a list of data indices with corresponding labels
    into subsets according to a dirichlet distribution with parameter
    alpha
    '''
    n_classes = train_labels.max()+1
    label_distribution = np.random.dirichlet([alpha]*n_clients, n_classes)

    class_idcs = [np.argwhere(train_labels[train_idcs] == y).flatten()
                  for y in range(n_classes)]

    client_idcs = [[] for _ in range(n_clients)]
    for c, fracs in zip(class_idcs, label_distribution):
        for i, idcs in enumerate(np.split(c, (np.cumsum(fracs)[:-1]*len(c)).astype(int))):
            client_idcs[i] += [idcs]

    client_idcs = [train_idcs[np.concatenate(idcs)] for idcs in client_idcs]

    return client_idcs
