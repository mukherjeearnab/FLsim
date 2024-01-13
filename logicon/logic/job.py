'''
Application Logic for Client Management
'''
import threading
from typing import Tuple
from state import job_state
from helpers.logging import logger


class Job(object):
    '''
    DistLearn Job Management Class
    '''

    def __init__(self, job_name: str, cluster_id: str, client_config: dict, worker_config: dict, cluster_config: dict, load_from_db=False):
        '''
        constructor
        '''
        self.job_name = job_name
        self.cluster_id = cluster_id

        if not load_from_db:
            self.modification_lock = threading.Lock()

            self.cluster_config = cluster_config[self.cluster_id]
            self.is_primary = True if self.cluster_config['upstream_cluster'] is None else False

            # populate client_config, if any of the clients are nodes
            self.client_configs = dict()
            self.clients = []
            self.sub_clusters = []
            for client_id in self.cluster_config['clients']:
                if client_id not in list(cluster_config.keys()):
                    self.client_configs[client_id] = client_config[client_id]
                    self.clients.append(client_id)
                else:
                    self.sub_clusters.append(client_id)

            # populate worker_config, if any of the clients are nodes
            self.worker_configs = dict()
            self.workers = []
            for worker_id in self.cluster_config['workers']:
                self.workers.append(worker_id)
                self.worker_configs[worker_id] = worker_config[worker_id]

            self.job_status = {
                'client_stage': 0,              # denotes the status of all the clients
                'worker_stage': 0,              # denotes the status of all the workers
                'download_jobsheet': False,     # flag to denote whether to download the job sheet
                'download_dataset': False,      # flag to denote whether to download the dataset
                'process_stage': 0,             # denotes the stage at which the job is
                'global_round': 0,              # denotes the current global round of federated training
                'abort': False,                 # denotes whether to abort the job or not
                'client_info': [                # stores the information of the client's individual status
                    # {
                    #     'client_id': 'client-0',
                    #     'status': 0,
                    #     'is_cluster': bool
                    # }
                ],
                'worker_info': [                # stores the information of the worker's individual status
                    # {
                    #     'worker_id': 'worker-0',
                    #     'status': 0,
                    # }
                ]
            }

            self.exec_params = {
                # trained and aggregated params are of schema {'client_id': {'param': Any, 'extra_data': Any}}
                'client_trained_params': dict(),
                'worker_aggregated_params': dict(),
                'global_model_param': {
                    'param': None,
                    'extra_data': None
                },
            }

            # finally update the state
            self._update_state()
        else:
            # load the existing state
            self._read_state()

    def _read_state(self, fetch_only=False):
        job_id = f'{self.job_name}#{self.cluster_id}'
        if job_id not in job_state:
            logger.error(
                f'Job [{self.job_name}] for Cluster [{self.cluster_id}] does not exists!')
            return None

        job_payload = job_state[job_id]

        # if only called for fetching data, and not updating the state of the job
        if fetch_only:
            return job_payload

        self.modification_lock = job_payload['modification_lock']
        self.is_primary = job_payload['is_primary']
        self.cluster_config = job_payload['cluster_config']
        self.client_configs = job_payload['client_configs']
        self.clients = job_payload['clients']
        self.sub_clusters = job_payload['sub_clusters']
        self.worker_configs = job_payload['worker_configs']
        self.workers = job_payload['workers']
        self.job_status = job_payload['job_status']
        self.exec_params = job_payload['exec_params']

    def _update_state(self):
        job_payload = {
            'modification_lock': self.modification_lock,
            'is_primary': self.is_primary,
            'cluster_config': self.cluster_config,
            'client_configs': self.client_configs,
            'clients': self.clients,
            'sub_clusters': self.sub_clusters,
            'worker_configs': self.worker_configs,
            'workers': self.workers,
            'job_status': self.job_status,
            'exec_params': self.exec_params
        }

        job_id = f'{self.job_name}#{self.cluster_id}'

        job_state[job_id] = job_payload

    def get_config(self, config_type: str):
        '''
        Get Configuration for type
        type = 'cluster' | 'client' | 'worker'
        '''

        payload = self._read_state(fetch_only=True)

        if payload is None:
            return None

        if config_type == 'cluster':
            return payload['cluster_config']
        elif config_type == 'client':
            return payload['client_configs']
        elif config_type == 'worker':
            return payload['worker_configs']
        else:
            return None

    def get_participants(self):
        '''
        Get all the id's of the participants
        Includes upstream cluster, sub-clusters, clients and workers
        '''

        payload = self._read_state(fetch_only=True)

        if payload is None:
            return None

        res = {
            'clients': payload['clients'],
            'sub_clusters': payload['sub_clusters'],
            'workers': payload['workers'],
            'upstream_cluster': payload['cluster_config']['upstream_cluster']
        }

        return res

    def get_job_status(self):
        '''
        Get the Job Status
        '''

        payload = self._read_state(fetch_only=True)

        if payload is None:
            return None

        return payload['job_status']

    def get_exec_params(self):
        '''
        Get the Job Execution Params
        '''

        payload = self._read_state(fetch_only=True)

        if payload is None:
            return None

        return payload['exec_params']

    def allow_jobsheet_download(self) -> bool:
        '''
        Allows to download Jobsheet for clients to prepare themselves.
        Basically modifies the job_status.download_jobsheet from False to True.
        Only work if process_stage is 0, client_stage is 0, worker_stage is 0,
        download_jobsheet is False and download_dataset is False. 
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        stage_flag = self.job_status['process_stage'] == 0 and self.job_status[
            'client_stage'] == 0 and self.job_status['worker_stage'] == 0
        download_flag = self.job_status['download_jobsheet'] is False and self.job_status['download_dataset'] is False

        if stage_flag and download_flag:
            self.job_status['download_jobsheet'] = True

            # method suffixed with update state and lock release
            self._update_state()
        else:
            # log output and set execution status to False
            logger.warning(
                f'''Cannot ALLOW JobSheet Download! 
                job_status.process_stage is {self.job_status["process_stage"]}, 
                job_status.client_stage is {self.job_status["client_stage"]},
                job_status.download_jobsheet is {self.job_status["download_jobsheet"]}, 
                job_status.download_dataset is {self.job_status["download_dataset"]}.''')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def allow_dataset_download(self) -> bool:
        '''
        Allows to download dataset for clients to prepare themselves from the data-distributor.
        Basically modifies the job_status.download_dataset from False to True.
        Only work if process_stage is 0, client_stage is 1, download_jobsheet is True and download_dataset is False.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        stage_flag = self.job_status['process_stage'] == 0 and self.job_status[
            'client_stage'] == 1 and self.job_status['worker_stage'] == 1
        download_flag = self.job_status['download_jobsheet'] is True and self.job_status['download_dataset'] is False

        if stage_flag and download_flag:
            self.job_status['download_dataset'] = True

            # method suffixed with update state and lock release
            self._update_state()
        else:
            # log output and set execution status to False
            logger.warning(
                f'''Cannot ALLOW Dataset Download! 
                job_status.process_stage is {self.job_status["process_stage"]}, 
                job_status.client_stage is {self.job_status["client_stage"]},
                job_status.download_jobsheet is {self.job_status["download_jobsheet"]}, 
                job_status.download_dataset is {self.job_status["download_dataset"]}.''')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def set_abort(self) -> bool:
        '''
        Sets the Abort Flag to True
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        self.job_status['abort'] = True
        self.job_status['process_stage'] = 3

        # method suffixed with update state and lock release
        self._update_state()

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def add_client(self, client_id: str, is_cluster: bool) -> bool:
        '''
        Adds a Client to the list of clients for the current job, only if job_status.process_stage is 0.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 0:
            self.job_status['client_info'].append({
                'client_id': client_id,
                'status': 0,
                'is_cluster': is_cluster
            })

            # method suffixed with update state and lock release
            self._update_state()
        else:
            # log output and set execution status to False
            logger.warning(
                f'''Cannot ADD Client!
                job_status.process_stage is {self.job_status["process_stage"]}.''')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def add_worker(self, worker_id: str) -> bool:
        '''
        Adds a Worker to the list of workers for the current job, only if job_status.process_stage is 0.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 0:
            self.job_status['worker_info'].append({
                'worker_id': worker_id,
                'status': 0
            })

            # method suffixed with update state and lock release
            self._update_state()
        else:
            # log output and set execution status to False
            logger.warning(
                f'''Cannot ADD Worker!
                job_status.process_stage is {self.job_status["process_stage"]}.''')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def update_client_status(self, client_id: str, client_status: int) -> Tuple[bool, int]:
        '''
        Updates the status of a client, based on their client_id and
        if all clients have the same status, the global client status, 
        i.e., job_status.client_stage is set as the status of the clients
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True
        next_signal = 0

        # method logic
        all_client_status = set()

        for i in range(len(self.job_status['client_info'])):
            # find the client and update their status
            if self.job_status['client_info'][i]['client_id'] == client_id:
                self.job_status['client_info'][i]['status'] = client_status

            # collect the status of all the clients
            all_client_status.add(
                self.job_status['client_info'][i]['status'])

        logger.info(
            f"Client [{client_id}] is at stage [{client_status}].")

        if len(all_client_status) == 1:
            self.job_status['client_stage'] = list(all_client_status)[0]
            logger.info(
                f"All clients are at Stage: [{self.job_status['client_stage']}]")
            next_signal = self._cw_stage_update_handler()

        # method suffixed with update state and lock release
        self._update_state()
        self.modification_lock.release()
        return exec_status, next_signal

    def update_worker_status(self, worker_id: str, worker_status: int) -> Tuple[bool, int]:
        '''
        Updates the status of a worker, based on their worker_id and
        if all workers have the same status, the global worker status, 
        i.e., job_status.worker_stage is set as the status of the workers
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True
        next_signal = 0

        # method logic
        all_worker_status = set()

        for i in range(len(self.job_status['worker_info'])):
            # find the worker and update their status
            if self.job_status['worker_info'][i]['worker_id'] == worker_id:
                self.job_status['worker_info'][i]['status'] = worker_status

            # collect the status of all the workers
            all_worker_status.add(
                self.job_status['worker_info'][i]['status'])

        logger.info(
            f"Worker [{worker_id}] is at stage [{worker_status}].")

        if len(all_worker_status) == 1:
            self.job_status['worker_stage'] = list(all_worker_status)[0]
            logger.info(
                f"All workers are at Stage: [{self.job_status['worker_stage']}]")
            next_signal = self._cw_stage_update_handler()

        # method suffixed with update state and lock release
        self._update_state()
        self.modification_lock.release()
        return exec_status, next_signal

    def _cw_stage_update_handler(self):
        '''
        If there are additional activities need to be performed
        after client stage updates, they are triggered from here.

        Signal Class:
        1XX : client + worker
        2XX : client
        3XX : worker
        '''
        client_stage = self.job_status['client_stage']
        worker_stage = self.job_status['worker_stage']

        if client_stage == 1 and worker_stage == 1:
            # returns signal to execute the following
            # send job download ack to upstream cluster
            # set download flag true (allow dataset download)
            return 101

        if client_stage == 2 and worker_stage == 2:
            # returns signal to execute the following
            # send dataset download ack to upstream cluster
            # set process_phase to 1 (allow start training)
            return 102

        if client_stage == 3:
            # returns signal to execute the following
            # update client / cluster status to upstream cluster
            return 201

        if worker_stage == 4:
            # returns signal to execute the following
            # execute the consensus to select global update param
            # update process_phase (or) continue training (or) upload global update to upstream cluster
            return 301

    def allow_start_training(self) -> bool:
        '''
        Wrapper around the _allow_start_training,
        to expose to external calls
        '''

        return self._allow_start_training(_internal=False)

    def _allow_start_training(self, _internal: bool) -> bool:
        '''
        Signal clients to start training by setting job_status.process_stage to 1.
        Only works if job_status.client_stage=2/4 and job_status.process_stage=0/2
        and job_status.worker_stage=2/4
        '''
        # method prefixed with locking and reading state
        if not _internal:
            self.modification_lock.acquire()
            self._read_state()
        exec_status = True

        # method logic
        process_stage = self.job_status['process_stage'] == 0 or self.job_status['process_stage'] == 2
        client_stage = self.job_status['client_stage'] == 2 or self.job_status['client_stage'] == 4
        worker_stage = self.job_status['worker_stage'] == 2 or self.job_status['worker_stage'] == 4

        if process_stage and client_stage and worker_stage:
            self.job_status['process_stage'] = 1
            # self.exec_params['client_model_params'] = []

            logger.info("Changed process_stage to 1, Start training.")

            # method suffixed with update state and lock release
            if not _internal:
                self._update_state()
        else:
            logger.warning(
                f'Cannot SET process_stage to 1 (InLocalTraining)!\nprocess_stage is {self.job_status["process_stage"]}\nclient_stage is {self.job_status["client_stage"]}\nworker_stage is {self.job_status["worker_stage"]}')
            exec_status = False

        # method suffixed with update state and lock release
        if not _internal:
            self.modification_lock.release()
        return exec_status

    def terminate_training(self) -> bool:
        '''
        Signal to Terminate the Training process. This sets the process_stage to 3, i.e., TrainingComplete
        Requires Clients to be waiting for Model Params, i.e., client_stage is 4,
        and Workers to be Aggregated Param Uploaded, i.e., worker_stage is 4,
        and process stage is at InCentralAggregation, i.e., process_stage is 2.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 2 and self.job_status['client_stage'] == 4 and self.job_status['worker_stage'] == 4:
            self.job_status['process_stage'] = 3

            # method suffixed with update state and lock release
            self._update_state()
        else:
            logger.warning(
                f'Cannot Terminate Training Process!\nprocess_stage is {self.job_status["process_stage"]}\nclient_stage is {self.job_status["client_stage"]}\nworker_stage is {self.job_status["worker_stage"]}')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def set_global_model_param(self, param: dict, extra_data: dict) -> bool:
        '''
        Set or Update the Global Model Parameters, for initial time, or aggregated update time.
        Only set, if process_stage is 0 or 2, i.e., NotStarted or InAggregation.

        Remember to call allow_start_training() to update the process_stage to 1,
        to signal Clients to download params and start training.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 0 or self.job_status['process_stage'] == 2:
            self.exec_params['global_model_param']['param'] = param
            self.exec_params['global_model_param']['extra_data'] = extra_data

            # empty out client and worker params
            self.exec_params['client_trained_params'] = dict()
            self.exec_params['worker_aggregated_params'] = dict()

            # increment global round
            self.job_status['global_round'] += 1

            logger.info(
                'Global Model Parameters are Set. Waiting for process_stage to be in [1] Local Training.')

            # set process stage to 1
            # self._allow_start_training(_internal=True)
            # NOTE: This will be triggered by the external process

            # method suffixed with update state and lock release
            self._update_state()
        else:
            logger.warning(
                f'Global model parameters NOT SET! process_phase is {self.job_status["process_phase"]}.')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def append_client_params(self, client_id: str, param: dict, extra_data: dict) -> bool:
        '''
        Append Trained Model Params from Clients to the exec_params.client_trained_params{}.
        Only works if job_status.worker_stage=2 and job_status.process_phase=1.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 1 and self.job_status['worker_stage'] == 2:
            # add client submitted parameters
            self.exec_params['client_trained_params'][client_id] = {
                'param': param,
                'extra_data': extra_data
            }

            logger.info(
                f"[{client_id}] submitted params. Total Params: {len(self.exec_params['client_trained_params'].keys())}/{len(self.clients)+len(self.sub_clusters)}")

            # if all the client's parameters are submitted, set process_phase to 2, i.e., InCentralAggregation
            if len(self.exec_params['client_trained_params'].keys()) == (len(self.clients)+len(self.sub_clusters)):
                self.job_status['process_phase'] = 2
                logger.info(
                    'All client params are submitted, signalling Federated Aggregation.')

            # method suffixed with update state and lock release
            self._update_state()
        else:
            logger.warning(
                f'Cannot APPEND client model params!\nprocess_stage is {self.job_status["process_stage"]}\nclient_stage is {self.job_status["client_stage"]}\nworker_stage is {self.job_status["worker_stage"]}')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status

    def append_worker_params(self, worker_id: str, param: dict, extra_data: dict) -> bool:
        '''
        Append Aggregated Model Params from Workers to the exec_params.worker_aggregated_params[].
        Only works if job_status.client_stage=4 and job_status.process_phase=2.
        '''
        # method prefixed with locking and reading state
        self.modification_lock.acquire()
        self._read_state()
        exec_status = True

        # method logic
        if self.job_status['process_stage'] == 2 and self.job_status['client_stage'] == 4:
            # add worker submitted parameters
            self.exec_params['worker_aggregated_params'][worker_id] = {
                'param': param,
                'extra_data': extra_data
            }

            logger.info(
                f"[{worker_id}] submitted params. Total Params: {len(self.exec_params['worker_aggregated_params'].keys())}/{len(self.workers)}")

            # check if all the worker's parameters are submitted
            if len(self.exec_params['worker_aggregated_params'].keys()) == (len(self.workers)):
                logger.info(
                    'All worker params are submitted, next is Consensus Exec.')

            # method suffixed with update state and lock release
            self._update_state()
        else:
            logger.warning(
                f'Cannot APPEND worker model params!\nprocess_stage is {self.job_status["process_stage"]}\nclient_stage is {self.job_status["client_stage"]}\nworker_stage is {self.job_status["worker_stage"]}')
            exec_status = False

        # method suffixed with update state and lock release
        self.modification_lock.release()
        return exec_status


CLIENT_STAGE = {
    0: 'Online',
    1: 'Ready With Jobsheet',
    2: 'Ready With Dataset',
    3: 'Busy In Training',
    4: 'Waiting For Params',
    5: 'Terminated'
}

WORKER_STAGE = {
    0: 'Online',
    1: 'Ready With Jobsheet',
    2: 'In Aggregation',
    3: 'Aggregated Params Uploaded',
    4: 'Busy In Concensus',
    5: 'Terminated'
}

PROCESS_STAGE = {
    0: 'Not Started',
    1: 'In Local Training',
    2: 'In Aggregation',
    3: 'Training Completed'
}
