'''
Dataset Configurator Module
Contains logic to structurally represent the dataset splits for a given cluster structure
'''
import json


def create_dist_tree(config: dict):
    '''
    Creates a Tree Representation of how 
    the dataset will be distributed within clusters

    0 : {
        distributor: diritchlet_dist,
        num_clients: 2,
        0: {
            distributor: random_dist,
            num_clients: 2,
        },
        1: {
            distributor: diritchlet_dist,
            num_clients: 2,
        }
    }
    '''

    root_node, structure = traverse_config_for_tree(config)

    return root_node, structure


def traverse_config_for_tree(config: dict):
    '''
    Traverse the configuration dict and create a tree of all the cluster nodes
    '''
    root_cluster, structure = None, dict()

    # find the root cluster (i.e., the root node)
    for cluster_id, cluster in config['clusters'].items():
        if cluster['upstream_cluster'] is None:
            root_cluster = cluster_id

    def traverse(cluster_id: str, config: dict, index: int, structure: dict):
        cluster = config['clusters'][cluster_id]

        structure[index] = dict()
        structure[index]['id'] = cluster_id
        structure[index]['distributor'] = cluster['dataset_params']['distribution']['distributor']['file']
        structure[index]['num_clients'] = len(cluster['clients'])
        structure[index]['clients'] = cluster['clients']

        for i, client_id in enumerate(cluster['clients']):
            if client_id in list(config['clusters'].keys()):
                traverse(client_id, config, i, structure[index])

    traverse(root_cluster, config, 0, structure)

    return root_cluster, structure
