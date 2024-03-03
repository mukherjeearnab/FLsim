'''
The Client Process Module
'''
from time import time, sleep
from env import env
from helpers.argsparse import args
from helpers.logging import logger
from helpers import p2p_store, perflog
from apps.client import handlers
from apps.common import getters, setters, listeners


def client_process(job_name: str, cluster_id: str) -> None:
    '''
    Client Process
    0. Wait for JobsheetDownload Flag
    1. Download Job Configuration
    2. ACK of Job Sheet Download (Client Status to 1)
        1. Initialize the Model and Obtain Intial Parameters
    3. Wait for DatasetDownload Flag
    4. Download the Dataset
        0. Download Dataset Metadata
            1. Scaffold Download Path and Directories
            2. Check OK File, and Determine if Required to Download Dataset
            3. Download Dataset if Required and OK File's timestamp
        1. Preprocess Dataset and Load it
    5. ACK of Dataset Download (Client Status to 2) & Send Back Initial Model (Global) Parameters
    6. Wait for process_stage to be 1
    7. Donwload Global Parameter
        1. Apply Parameter Mixing
    8. Update Client Status to 3
    9. Load Model and Start Local Training
        1. Test Trained Model
        2. Add Test Performance Metrics to PerfLog
    10. Upload Trained Model Parameter
    11. Update Client Status to 4
    12. Wait for client_stage to be 4
    13. Wait for process_stage to be 1 or 3
    14. If process_stage is 1, start again from step 7, 
        else Update Client Status to 5 and exit
    '''

    node_id = args['node_id']
    node_type = 'client'
    wait_factor = int(node_id.split('_')[1])%10

    global_round = 1
    extra_data = {
        'round_info': {'current_round': global_round},
        'global_extra_data': None
    }

    sync_delay = 5 + env['DELAY'] * wait_factor
    logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
    sleep(sync_delay)

    # 0. Wait for JobsheetDownload Flag
    listeners.wait_for_jobsheet_flag(job_name, cluster_id, node_type)

    logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
    sleep(sync_delay)

    # 1. Download Job Configuration
    manifest = getters.get_job_config(job_name, cluster_id, node_type)

    # 2. ACK of Job Sheet Download (Client Status to 1)
    setters.update_node_status(job_name, cluster_id, node_type, 1)
    logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
    sleep(sync_delay)
    listeners.wait_for_node_stage(job_name, cluster_id, node_type, 1)

    # 2.1 Initialize the Model and Obtain Intial Parameters
    strategy = handlers.init_strategy(
        job_name, cluster_id, node_type, manifest)

    # obtain initial global state of the model
    initial_global_state = strategy.get_base64_global_payload()

    logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
    sleep(sync_delay)

    # 3. Wait for DatasetDownload Flag
    listeners.wait_for_dataset_flag(job_name, cluster_id, node_type)

    # 4. Download the Dataset
    # 4.0. Download Dataset Metadata
    dataset_path, file_path, timestamp = handlers.download_dataset_metadata(
        job_name, cluster_id, node_type)

    # 4.0.3 Download Dataset if Required and OK File's timestamp
    file_name, dataset_path = handlers.download_dataset(
        job_name, cluster_id, node_type, dataset_path, file_path, timestamp)

    # 4.1. Preprocess Dataset and Load it
    train_set, test_set = handlers.load_dataset(job_name, cluster_id, node_type,
                                                file_name, dataset_path, strategy)

    # also load the dataset into the strategy object
    strategy.load_dataset(train_set, test_set)

    # 5. ACK of Dataset Download (Client Status to 2) & Send Back Initial Model (Global) Parameters
    # 5.1 Upload Initial Model (Global) Parameters to P2P Store
    init_global_state_key = p2p_store.setv(initial_global_state)
    # 5.2 ACK of Dataset Download (Client Status to 2)
    setters.update_node_status(
        job_name, cluster_id, node_type, 2)
    logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
    sleep(sync_delay)
    listeners.wait_for_node_stage(job_name, cluster_id, node_type, 2)

    # 6. Wait for process_stage to be 1
    _, global_round, cluster_epoch = listeners.wait_for_start_end_training(
        job_name, cluster_id, node_type)

    # Process Loop
    while True:
        # set start time
        start_time = time()

        # 7. Donwload Global Parameter
        global_state = handlers.get_global_state(
            job_name, cluster_id, node_type)
        strategy.load_base64_state(global_state)

        # 7.1. Apply Parameter Mixing
        strategy.parameter_mixing()

        # 8. Update Client Status to 3
        setters.update_node_status(job_name, cluster_id, node_type, 3)
        logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
        sleep(sync_delay)
        listeners.wait_for_node_stage(job_name, cluster_id, node_type, 3)

        # 8.1. Test Trained Model On Global Params
        metrics = handlers.test_model(job_name, cluster_id, node_type,
                                      strategy)

        # 8.2. Add Test Performance Metrics to PerfLog
        perflog.add_record(job_name, cluster_id, node_id, node_type,
                           global_round, cluster_epoch, metrics, -1)

        # 9. Load Model and Start Local Training
        handlers.train_model(job_name, cluster_id, node_type,
                             strategy)

        # 9.1. Test Trained Model
        metrics = handlers.test_model(job_name, cluster_id, node_type,
                                      strategy)

        # calculate round time
        end_time = time()
        time_delta = (end_time - start_time)
        logger.info(f'[{node_type}] Total Round Time: {time_delta} s')

        # 9.2. Add Test Performance Metrics to PerfLog
        perflog.add_record(job_name, cluster_id, node_id, node_type,
                           global_round, cluster_epoch, metrics, time_delta)

        # 10. Upload Trained Model Parameter
        trained_local_state = strategy.get_base64_local_payload()
        trained_state_key = p2p_store.setv(trained_local_state)
        setters.append_node_params(
            job_name, cluster_id, node_type, trained_state_key)

        # 11. Update Client Status to 4
        setters.update_node_status(job_name, cluster_id, node_type, 4)
        logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
        sleep(sync_delay)

        # 12. Wait for client_stage to be 4 and Process Phase to be 2
        # listeners.wait_for_node_stage(job_name, cluster_id, node_type, 4)
        logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
        sleep(sync_delay)
        listeners.wait_for_aggregation_phase(job_name, cluster_id, node_type)

        logger.info(f'[{node_type}] Sleeping for {sync_delay} seconds')
        sleep(sync_delay)
        # 13. Wait for process_stage to be 1 or 3
        process_stage, global_round, cluster_epoch = listeners.wait_for_start_end_training(
            job_name, cluster_id, node_type)

        # 14. If process_stage is 1, start again from step 7,
        #     else Update Client Status to 5 and exit
        if process_stage == 1:
            start_time = time()

        if process_stage == 3:
            logger.info(
                f"[{node_type}] Job [{job_name}] terminated. Exiting Process.")
            setters.update_node_status(job_name, cluster_id, node_type, 5)
            break
