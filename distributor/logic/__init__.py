'''
Key Value Store Class
'''
import traceback
import threading
from hashlib import md5
from typing import Tuple, Union
from job_object import Job
from data_ops import create_central_testset, train_test_split
from helpers.logging import logger
from helpers.dynamod import load_module
from helpers.file import torch_write, torch_read, set_OK_file, check_OK_file
from helpers.file import create_dir_struct, file_exists


class DatasetDistributor(object):
    '''
    Dataset Distributor Management Class
    '''

    def __init__(self):
        self.jobs = dict()
        self.locks = dict()

    def register_n_prepare(self, job_name: str, manifest: dict) -> Tuple[bool, str]:
        '''
        Register a Job and prepare the dataset based on the given manifest
        '''
        if job_name in self.jobs:
            return False, "Job already registered."

        self.jobs[job_name] = Job(job_name, manifest)

        # 1. prepare root dataset
        root_train_set, root_test_set = self._prepare_root_dataset(
            self.jobs[job_name])
        # 2. recursively prepare chunks for the clusters
        self._prepare_chunk_datasets(
            self.jobs[job_name], root_train_set, root_test_set)
        # (while doing so, do map chunk to nodes (client / workers))

    def _prepare_root_dataset(self, job: Job):
        '''
        Function to prepare the root dataset
        '''
        dataset_prep_file = job.manifest[0]['params']['prep']['content']
        job.dataset_prep_mod = job.manifest[0]['params']['prep']['file']
        job.dataset_root_path = f"./datasets/deploy/{job.dataset_prep_mod}/root"

        # create the directory structures
        create_dir_struct(job.dataset_root_path)

        # if root dataset is not already present, prepare it
        if not check_OK_file(job.dataset_root_path):
            # load the dataset prep module
            try:
                dataset_prep_module = load_module(
                    'dataset_prep', dataset_prep_file)

                # obtain the dataset as data and labels
                (train_set, test_set) = dataset_prep_module.prepare_dataset()
            except Exception:
                logger.info(
                    f'Error Executing Dataset Prep Module.\n{traceback.format_exc()}')

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
        else:
            logger.info('Root Dataset already present. Loading it from disk.')
            train_set = torch_read('train_dataset.tuple',
                                   job.dataset_root_path)
            if file_exists(f'{job.dataset_root_path}/test_dataset.tuple'):
                test_set = torch_read(
                    'test_dataset.tuple', job.dataset_root_path)
            else:
                test_set = None

        return train_set, test_set

    def _prepare_chunk_datasets(self, job: Job, train_set, test_set):
        '''
        Recursively Prepare CHunk Datasets
        '''
        chunk_path = f"./datasets/deploy/{job.dataset_prep_mod}/chunks"
        self._recursive_chunking(
            job, job.manifest[0], chunk_path, train_set, test_set)

    def _recursive_chunking(self, job: Job, cluster: dict, chunk_path: str, train_set, test_set):
        '''
        TODO
        '''

        logger.info(f"Working on cluster [{cluster['id']}]")

        dynamic_dist = 'chunks' not in cluster['params']['distribution']
        chunk_save_path = None

        # create chunk dir name (if client weights are specified)
        if not dynamic_dist:
            chunk_dir_name = f"{cluster['params']['distribution']['distributor']}"
            chunk_dir_name = chunk_dir_name + "".join(
                [f"-{chunk}" for chunk in cluster['params']['distribution']['chunks']])
            chunk_save_path = f"{chunk_path}/{chunk_dir_name}"

        extra_params = cluster['params']['distribution']['extra_params']
        num_clients = cluster['num_clients']
        chunks_ratio = [
            0.1 for _ in num_clients] if dynamic_dist else cluster['params']['distribution']['chunks']

        # if chunk datasets are already not prepared, then prepare them
        if dynamic_dist or (not check_OK_file(chunk_save_path)):
            # load the dataset prep module
            try:
                distributor_module = load_module(
                    'distributor', cluster['params']['distribution']['distributor']['content'])

                # obtain the dataset as data and labels
                train_chunks, new_client_weights = distributor_module.distribute_into_client_chunks(train_set,
                                                                                                    chunks_ratio,
                                                                                                    extra_params, train=True)
                cluster['params']['distribution']['chunks'] = new_client_weights
            except:
                logger.info(
                    f'Error Executing Dataset Distributor. Terminating...\n{traceback.format_exc()}')
                return

            # if dynamic distribution, update the dist chunk dir name with updated weights
            if dynamic_dist:
                chunk_dir_name = f"{cluster['params']['distribution']['distributor']}/dist"
                chunk_dir_name = chunk_dir_name + "".join(
                    [f"-{chunk}" for chunk in cluster['params']['distribution']['chunks']])
                chunk_save_path = f"{chunk_path}/{chunk_dir_name}"

            # check if already done with distribution
            if check_OK_file(chunk_save_path):
                logger.info('Chunks already present. Skipping...')
            else:
                create_dir_struct(chunk_save_path)

                if test_set is not None:
                    test_chunks, _ = distributor_module.distribute_into_client_chunks(test_set,
                                                                                      chunks_ratio,
                                                                                      extra_params)

                # if test set is not available, split the chunks into train and test sets
                if test_set is None:
                    split_ratio = list(
                        cluster['params']['train_test_split'].values())
                    chunks = [train_test_split(chunk, split_ratio)
                              for chunk in train_chunks]
                else:  # if test set is available, merge the train-test chunks into one
                    chunks = list(zip(train_chunks, test_chunks))

                # create the global test set
                global_test_set = create_central_testset(
                    [chunk[1] for chunk in chunks])

                # saving chunks and global test dataset to disk
                try:
                    # save the chunks dataset to disk
                    for i in range(num_clients):
                        # client = f'client-{i+1}'
                        # save the dataset to disk
                        torch_write(f'{i}.tuple',
                                    chunk_save_path,
                                    chunks[i])

                        logger.info(
                            f'Saved Chunk for {i+1}th Client with size {len(chunks[i][0][1])}, {len(chunks[i][1][1])}')

                    # saving global test dataset to disk
                    torch_write('global_test.tuple',
                                chunk_save_path,
                                global_test_set)

                    logger.info(
                        f'Saved Global Test Set with size {len(global_test_set[1])}')

                    # set the OK file
                    set_OK_file(chunk_save_path)
                    logger.info(
                        f"Dataset Client Chunks and Global Set Saved Successfully for Cluster [{cluster['id']}]!")
                except Exception:
                    logger.error(
                        f'Error Saving Chunked Dataset to disk!\n{traceback.format_exc()}')

            ############################
            # The Recursive Part
            ############################
            job.cluster2chunk_mapping[cluster['id']] = {
                'global_test': f"{chunk_save_path}/global_test.tuple"
            }
            # recursively save the chunks for the sub clusters
            for i in range(num_clients):
                # add the client chunk's path to the cluster2chunk mapping
                job.cluster2chunk_mapping[cluster['id']][
                    cluster['clients'][i]] = f"{chunk_save_path}/{i}.tuple"

                # if client is not a cluster, skip the rest of the loop
                # no need to recursively split into chunks
                if i not in cluster:
                    continue

                chunk = torch_read(f'{i}.tuple',
                                   chunk_save_path)

                logger.info(f'Moving to sub-cluster {i}th Cluster')
                self._recursive_chunking(
                    job, cluster[i], chunk_save_path, chunk[0], chunk[1])
