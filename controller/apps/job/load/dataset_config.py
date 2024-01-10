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

    structure = dict()
    node_dir = dict()

    root_node = traverse_config_for_tree(config, node_dir)

    # print(node_dir[root_node])

    recursive_struct_finder(node_dir[root_node], config, structure, 0, set())

    return structure


def traverse_config_for_tree(config: dict, node_dir: dict):
    '''
    Traverse the configuration dict and create a tree of all the cluster nodes
    '''
    root_cluster = None
    for cluster_id, cluster in config['clusters'].items():
        node_dir[cluster_id] = ClusterNode(cluster_id)
        if cluster['upstream_cluster'] is None:
            root_cluster = cluster_id

    def traverse(cluster_id: str, config: dict, visited: set):
        if cluster_id in visited:
            return

        visited.add(cluster_id)

        cluster = config['clusters'][cluster_id]

        for client_id in cluster['clients']:
            if client_id in list(config['clusters'].keys()):
                node_dir[cluster_id].children.append(node_dir[client_id])
                traverse(client_id, config, visited)

    traverse(root_cluster, config, set())

    return root_cluster


def recursive_struct_finder(root, config: dict, structure: dict, index, visited):
    '''
    Recursively find the distribution structure
    '''
    if root.id in visited:
        return

    visited.add(root.id)

    structure[index] = dict()
    structure[index]['id'] = root.id
    structure[index]['distributor'] = config['clusters'][root.id]['dataset_params']['distribution']['distributor']['file']
    structure[index]['num_clients'] = len(
        config['clusters'][root.id]['clients'])
    structure[index]['clients'] = config['clusters'][root.id]['clients']

    for i, cluster in enumerate(root.children):
        recursive_struct_finder(cluster, config, structure[index], i, visited)


class ClusterNode:
    def __init__(self, id: str):
        self.id = id
        self.children = []
