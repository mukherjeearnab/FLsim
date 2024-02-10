'''
Key Value Store Class
'''
import traceback
import dill
import base64
import hashlib
from typing import Tuple, Any, Union
from logic.job_object import Job
from logic.data_ops import create_central_testset, train_test_split
from helpers.logging import logger
from helpers.file import torch_write, torch_read, set_OK_file, check_OK_file
from helpers.file import create_dir_struct, file_exists


class DatasetDistributor(object):
    '''
    Dataset Distributor Management Class
    '''

    def __init__(self):
        self.jobs = dict()
        self.locks = dict()

    def delete_job(self, job_name: str) -> bool:
        '''
        Delete dataset config for a given job
        '''
        if job_name not in self.jobs:
            return False

        del self.jobs[job_name]
        return True

    def get_dataset_metadata(self, job_name: str, cluster_id: str, metadata: str) -> Union[str, None]:
        '''
        Get the dataset metadata based on the cluster_id, i.e.: 
        metadata == client_id ==> returns the dataset chunk path for the client 
        metadata == 'global_test' ==> returns the dataset chunk path for the global_test (for workers) 
        metadata == 'ok_file' ==> returns the ok_file path for the dataset chunk
        metadata == 'weights' ==> returns the weights of the clients
        metadata == 'complete' ==> returns the complete cluster2chunk_mapping object
        '''

        if job_name not in self.jobs:
            return None

        if metadata == 'complete':
            return self.jobs[job_name].cluster2chunk_mapping

        if cluster_id not in self.jobs[job_name].cluster2chunk_mapping:
            return None

        if metadata not in self.jobs[job_name].cluster2chunk_mapping[cluster_id]:
            return None

        return self.jobs[job_name].cluster2chunk_mapping[cluster_id][metadata]

    def register_n_prepare(self, job_name: str, manifest: dict) -> Tuple[bool, str]:
        '''
        Register a Job and prepare the dataset based on the given manifest
        '''
        if job_name in self.jobs:
            return False, "Job already registered."

        self.jobs[job_name] = Job(job_name, manifest)

        # 1. prepare root dataset
        root_train_set, root_test_set, status = self._prepare_root_dataset(
            self.jobs[job_name])

        if status != 0:
            if status == 1:
                return False, "Error Executing Dataset Prep Module."
            if status == 2:
                return False, "Error Saving Prepared Dataset to disk!"

        # 2. recursively prepare chunks for the clusters
        # (while doing so, do map chunk to nodes (client / workers))
        status = self._prepare_chunk_datasets(
            self.jobs[job_name], root_train_set, root_test_set)

        if status != 0:
            if status == 1:
                return False, "Error Executing Distributor Module."
            if status == 2:
                return False, "Error Saving Chunked Dataset to disk!"

        return True, "Successfully Prepared Dataset for Job!"

    def _prepare_root_dataset(self, job: Job) -> Tuple[Any, Any, int]:
        '''
        Function to prepare the root dataset
        '''
        dataset_definition = job.manifest['0']['params']['dataset']['definition']
        DatasetClass = dill.loads(
            base64.b64decode(dataset_definition.encode()))
        dataset = DatasetClass(job.manifest['0']['params']['distribution'])
        job.manifest['0']['params']['dataset']['object'] = dataset

        job.dataset_prep_mod = dataset.dataset_name
        job.dataset_root_path = f"./datasets/deploy/{job.dataset_prep_mod}/root"

        # create the directory structures
        create_dir_struct(job.dataset_root_path)

        # if root dataset is not already present, prepare it
        if not check_OK_file(job.dataset_root_path):
            # load the dataset prep module
            try:
                # obtain the dataset as data and labels
                (train_set, test_set) = dataset.prepare_root_dataset()
            except Exception:
                logger.info(
                    f'Error Executing Dataset Prep Module.\n{traceback.format_exc()}')
                return None, None, 1

            # saving dataset file to disk
            try:
                # save the train dataset to disk
                torch_write('train_dataset.tuple',
                            job.dataset_root_path, train_set)
                logger.info('Saved training dataset to disk!')

                # if test dataset is available, save it to disk
                if test_set is not None:
                    torch_write('test_dataset.tuple',
                                job.dataset_root_path, test_set)
                    logger.info('Saved testing dataset to disk!')

                # set the OK file
                set_OK_file(job.dataset_root_path)
                logger.info('Prepared Root Dataset Saved Successfully!')
            except Exception:
                logger.error(
                    f'Error Saving Prepared Dataset to disk!\n{traceback.format_exc()}')
                return None, None, 2
        else:
            logger.info('Root Dataset already present. Loading it from disk.')
            train_set = torch_read('train_dataset.tuple',
                                   job.dataset_root_path)
            if file_exists(f'{job.dataset_root_path}/test_dataset.tuple'):
                test_set = torch_read(
                    'test_dataset.tuple', job.dataset_root_path)
            else:
                test_set = None

        return train_set, test_set, 0

    def _prepare_chunk_datasets(self, job: Job, train_set, test_set) -> int:
        '''
        Recursively Prepare Chunk Datasets
        '''
        chunk_path = f"./datasets/deploy/{job.dataset_prep_mod}/chunks"
        status = self._recursive_chunking(
            job, job.manifest['0'], chunk_path, train_set, test_set)

        return status

    def _recursive_chunking(self, job: Job, cluster: dict, chunk_path: str, train_set, test_set) -> int:
        '''
        Recursively Prepare the chunks and organize them into a directory structure
        '''

        logger.info(f"Working on cluster [{cluster['id']}]")
        return_status = 0

        dataset_definition = cluster['params']['dataset']['definition']
        DatasetClass = dill.loads(
            base64.b64decode(dataset_definition.encode()))
        dataset = DatasetClass(cluster['params']['distribution'])
        cluster['params']['dataset']['object'] = dataset

        dynamic_dist = dataset.dynamic_weights
        chunk_save_path = None

        extra_params = cluster['params']['distribution']['extra_params']
        num_clients = cluster['num_clients']
        dataset.client_weights = [0.1 for _ in range(
            num_clients)] if dynamic_dist else dataset.client_weights

        # if chunk datasets are already not prepared, then prepare them
        if dynamic_dist or (not check_OK_file(chunk_save_path)):
            # load the dataset prep module
            try:
                # obtain the dataset as data and labels
                train_chunks, _ = dataset.distribute_into_chunks(train_set)
            except:
                logger.info(
                    f'Error Executing Dataset Distributor. Terminating...\n{traceback.format_exc()}')
                return 1

            # create the chunk dir name
            chunk_dir_name = f"{dataset.distribution_method}/dist-"
            dist = "".join(
                [f"-{chunk}" for chunk in dataset.client_weights])
            chunk_dir_name = chunk_dir_name + \
                hashlib.md5(dist.encode()).hexdigest()
            chunk_save_path = f"{chunk_path}/{chunk_dir_name}"

            # check if already done with distribution
            if check_OK_file(chunk_save_path):
                logger.info('Chunks already present. Skipping...')
            else:
                create_dir_struct(chunk_save_path)

                if test_set is not None:
                    try:
                        # obtain the dataset as data and labels
                        test_chunks, _ = dataset.distribute_into_chunks(
                            test_set)
                    except:
                        logger.info(
                            f'Error Executing Dataset Distributor. Terminating...\n{traceback.format_exc()}')
                        return 1

                # if test set is not available, split the chunks into train and test sets
                if test_set is None:
                    chunks = [train_test_split(dataset, chunk)
                              for chunk in train_chunks]
                else:  # if test set is available, merge the train-test chunks into one
                    chunks = list(zip(train_chunks, test_chunks))

                # create the global test set
                global_test_set = create_central_testset(dataset,
                                                         [chunk[1] for chunk in chunks])

                # saving chunks and global test dataset to disk
                try:
                    # save the chunks dataset to disk
                    for i in range(num_clients):
                        # client = f'client-{i+1}'
                        # save the dataset to disk
                        create_dir_struct(f'{chunk_save_path}/{i}')
                        torch_write('index.tuple',
                                    f'{chunk_save_path}/{i}',
                                    chunks[i])

                        logger.info(
                            f'Saved Chunk for {i+1}th Client with size {len(chunks[i][0][1])}, {len(chunks[i][1][1])}')

                    # saving global test dataset to disk
                    torch_write('global_test.tuple',
                                chunk_save_path,
                                global_test_set)

                    logger.info(
                        f'Saved Global Test Set with size {len(global_test_set[1])}')

                    # write the distribution ratio file
                    with open(f'{chunk_save_path}/distribution_ratio.txt', 'w', encoding='utf8') as f:
                        f.writelines(
                            [f'{chunk}\n' for chunk in dataset.client_weights])

                    # set the OK file
                    set_OK_file(chunk_save_path)
                    logger.info(
                        f"Dataset Client Chunks and Global Set Saved Successfully for Cluster [{cluster['id']}]!")
                except Exception:
                    logger.error(
                        f'Error Saving Chunked Dataset to disk!\n{traceback.format_exc()}')
                    return 2
        else:
            logger.info('Chunks already present. Skipping...')
        ############################
        # The Recursive Part
        ############################
        # define cluster to chunk mapping for the cluster
        client_weights = {node_id: weight for node_id,
                          weight in zip(cluster['clients'], dataset.client_weights)}

        job.cluster2chunk_mapping[cluster['id']] = {
            'global_test': f"{chunk_save_path}/global_test.tuple",
            'ok_file': f"{chunk_save_path}",
            'weights': client_weights
        }
        # recursively save the chunks for the sub clusters
        for i in range(num_clients):
            # add the client chunk's path to the cluster2chunk mapping
            job.cluster2chunk_mapping[cluster['id']][
                cluster['clients'][i]] = f"{chunk_save_path}/{i}/index.tuple"

            # if client is not a cluster, skip the rest of the loop
            # no need to recursively split into chunks
            if f'{i}' not in cluster:
                continue

            chunk = torch_read('index.tuple',
                               f'{chunk_save_path}/{i}')

            logger.info(f'Moving to sub-cluster {i}th Cluster')
            return_status = self._recursive_chunking(
                job, cluster[f'{i}'], f'{chunk_save_path}/{i}', chunk[0], chunk[1])

        return max(0, return_status)
