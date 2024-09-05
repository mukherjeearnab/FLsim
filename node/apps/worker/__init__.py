'''
The Worker Process Module
'''
from time import time, sleep
from env import env
from helpers.argsparse import args
from helpers.logging import logger
from helpers import p2p_store, perflog
from apps.worker import handlers
from apps.common import getters, setters, listeners


def worker_process(job_name: str, cluster_id: str) -> None:
    '''
    Worker Process
    0. Wait for JobsheetDownload Flag
    1. Download Job Configuration
    2. ACK of Job Sheet Download (Worker Status to 1)
        1. Initialize the Model and Obtain Intial Parameters
    3. Wait for DatasetDownload Flag
    4. Download the Dataset
        0. Download Dataset Metadata
            1. Scaffold Download Path and Directories
            2. Check OK File, and Determine if Required to Download Dataset
            3. Download Dataset if Required and OK File's timestamp
        1. Preprocess Dataset and Load it
    5. ACK of Dataset Download (Worker Status to 2) & Send Back Initial Model (Global) Parameters
    6. Wait for process_stage to be 2
    7. Donwload All Trained Client Parameter(s) 
        1. Apply Parameter Mixing
    8. Update Worker Status to 3
    9. Start Aggregation Process
        1. Test Aggregated Model
        2. Add Test Performance Metrics to PerfLog
    10. Upload Aggregated Model Parameter
    11. Update Worker Status to 4
    12. Wait for worker_stage to be 4 and update to 2
    13. Wait for process_stage to be 1 or 3
    14. Add Global Parameter to Perflog and Commit Perflog
    15. If process_stage is 1, start again from step 6, 
        else Update Worker Status to 5 and exit
    '''

    node_id = args['node_id']
    node_type = 'worker'

    global_round = 1
    cluster_epoch = 1
    extra_data = {
        'round_info': {'current_round': global_round},
        'global_extra_data': None
    }

    startup_delay = env['DELAY'] * 5
    logger.info(f'[{node_type}] Sleeping for {startup_delay} seconds')
    sleep(startup_delay)

    # 0. Wait for JobsheetDownload Flag
    listeners.wait_for_jobsheet_flag(job_name, cluster_id, node_type)

    # 1. Download Job Configuration
    manifest = getters.get_job_config(job_name, cluster_id, node_type)

    # 2. ACK of Job Sheet Download (Client Status to 1)
    setters.update_node_status(job_name, cluster_id, node_type, 1)
    listeners.wait_for_node_stage(job_name, cluster_id, node_type, 1)

    # 2.1 Initialize the Model and Obtain Intial Parameters
    strategy = handlers.init_strategy(
        job_name, cluster_id, node_type, manifest)

    # obtain initial global state of the model
    initial_global_state = strategy.get_base64_global_payload()

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
    global_test_set = handlers.load_dataset(job_name, cluster_id, node_type,
                                            file_name, dataset_path)

    # also load the dataset into the strategy object
    strategy.load_dataset(None, global_test_set)

    # 5. ACK of Dataset Download (Client Status to 2) & Send Back Initial Model (Global) Parameters
    # 5.1 Upload Initial Model (Global) Parameters to P2P Store
    init_global_state_key = p2p_store.setv(initial_global_state)
    # 5.2 ACK of Dataset Download (Client Status to 2)
    setters.update_node_status(
        job_name, cluster_id, node_type, 2, {'initial_param': init_global_state_key})
    listeners.wait_for_node_stage(job_name, cluster_id, node_type, 2)

    # set start time
    start_time = time()

    # Process Loop
    while True:
        # 6. Wait for process_stage to be 2
        listeners.wait_for_aggregation_phase(job_name, cluster_id, node_type)

        # 7. Donwload All Trained Client Parameter(s)
        client_params = handlers.get_client_params(
            job_name, cluster_id, node_type)

        # 8. Update Worker Status to 3
        setters.update_node_status(job_name, cluster_id, node_type, 3)
        listeners.wait_for_node_stage(job_name, cluster_id, node_type, 3)
        listeners.wait_for_scheduled_execution(job_name, cluster_id, node_type)

        # 9. Start Aggregation Process
        handlers.run_aggregator(job_name, cluster_id, node_type,
                                strategy, client_params)

        # 9.1. Test Aggregated Model
        metrics = handlers.test_model(job_name, cluster_id, node_type,
                                      strategy)

        # calculate round time
        end_time = time()
        time_delta = (end_time - start_time)
        logger.info(f'[{node_type}] Total Round Time: {time_delta} s')

        # 9.2. Add Test Performance Metrics to PerfLog
        perflog.add_record(job_name, cluster_id, node_id, node_type,
                           global_round, cluster_epoch, metrics, time_delta)

        # SLEEP FOR A WHILE FOR THE CLIENTS TO GET THEIR SIGNALLING UPDATED
        logger.info('Sleeping for 60 seconds.')
        sleep(30)

        # 10. Upload Aggregated Model Parameter
        aggregated_global_state = strategy.get_base64_global_payload()
        agg_global_state_key = p2p_store.setv(aggregated_global_state)
        setters.append_node_params(
            job_name, cluster_id, node_type, agg_global_state_key)

        # 11. Update Worker Status to 4
        setters.update_node_status(job_name, cluster_id, node_type, 4)

        # 12. Wait for worker_stage to be 4
        listeners.wait_for_node_stage(job_name, cluster_id, node_type, 4)

        # 13. Wait for process_stage to be 1 or 3
        process_stage, global_round, cluster_epoch = listeners.wait_for_start_end_training(
            job_name, cluster_id, node_type)

        # 14. Add Global Parameter to Perflog and Commit Perflog
        global_param = handlers.get_global_state(
            job_name, cluster_id, node_type)
        perflog.add_params(
            job_name, global_round-1, global_param)
        perflog.save_logs(job_name)

        # 15. If process_stage is 1, start again from step 6,
        #     else Update Worker Status to 5 and exit
        if process_stage == 1:
            start_time = time()

            # memory profiling for auto assignment of nodes to machines
            # import resource
            # print("[W] MAX RESOURCE USAGE", resource.getrusage(
            #     resource.RUSAGE_SELF).ru_maxrss)

        if process_stage == 3:
            logger.info(
                f"[{node_type}] Job [{job_name}] terminated. Exiting Process.")
            setters.update_node_status(job_name, cluster_id, node_type, 5)
            perflog.terminate(job_name)
            break
