'''
The Client Process Module
'''
from time import time
from copy import deepcopy
from helpers.argsparse import args
from helpers.logging import logger
from helpers import p2p_store, perflog
from helpers.converters import get_base64_state_dict, set_base64_state_dict
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

    global_round = 1
    extra_data = {
        'round_info': {'current_round': global_round},
        'global_extra_data': None
    }

    # 0. Wait for JobsheetDownload Flag
    listeners.wait_for_jobsheet_flag(job_name, cluster_id, node_type)

    # 1. Download Job Configuration
    manifest = getters.get_job_config(job_name, cluster_id, node_type)

    # 2. ACK of Job Sheet Download (Client Status to 1)
    setters.update_node_status(job_name, cluster_id, node_type, 1)

    # 2.1 Initialize the Model and Obtain Intial Parameters
    local_model = handlers.init_model(
        job_name, cluster_id, manifest, node_type)

    # set global and prev local model
    global_model = deepcopy(local_model)
    prev_local_model = deepcopy(local_model)

    # obtain parameters of the model
    previous_param = get_base64_state_dict(prev_local_model)

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
                                                file_name, dataset_path, manifest)

    # also create the data loaders for the train set and test set
    train_loader, test_loader = handlers.create_data_loaders(
        train_set, test_set, manifest)

    # 5. ACK of Dataset Download (Client Status to 2) & Send Back Initial Model (Global) Parameters
    # 5.1 Upload Initial Model (Global) Parameters to P2P Store
    init_param_key = p2p_store.setv(previous_param)
    # 5.2 ACK of Dataset Download (Client Status to 2)
    setters.update_node_status(
        job_name, cluster_id, node_type, 2, {'initial_param': init_param_key})

    # 6. Wait for process_stage to be 1
    listeners.wait_for_start_end_training(job_name, cluster_id, node_type)

    # Process Loop
    while True:
        # set start time
        start_time = time()

        # 7. Donwload Global Parameter
        global_param, global_extra_data = handlers.get_global_param(
            job_name, cluster_id, node_type)
        set_base64_state_dict(global_model, global_param)
        extra_data['global_extra_data'] = global_extra_data

        # 7.1. Apply Parameter Mixing
        curr_param = handlers.parameter_mixing(
            job_name, cluster_id, manifest, node_type, global_model, prev_local_model)

        # update the parameters local and prev local models
        local_model.load_state_dict(curr_param)
        set_base64_state_dict(prev_local_model, previous_param)

        # 8. Update Client Status to 3
        setters.update_node_status(job_name, cluster_id, node_type, 3)

        # 9. Load Model and Start Local Training
        handlers.train_model(job_name, cluster_id, manifest, node_type, train_loader,
                             local_model, global_model, prev_local_model, extra_data)

        # 9.1. Test Trained Model
        metrics = handlers.test_model(job_name, cluster_id, manifest, node_type,
                                      local_model, test_loader)

        # calculate round time
        end_time = time()
        time_delta = (end_time - start_time)
        logger.info(f'Total Round Time: {time_delta} s')

        # 9.2. Add Test Performance Metrics to PerfLog
        perflog.add_record(node_id, job_name, metrics,
                           global_round, time_delta)

        # 10. Upload Trained Model Parameter
        curr_param = get_base64_state_dict(local_model)
        trained_param_key = p2p_store.setv(curr_param)
        extra_data_key = p2p_store.setv(global_extra_data)
        setters.append_node_params(
            job_name, cluster_id, node_type, trained_param_key, extra_data_key)

        # 11. Update Client Status to 4
        setters.update_node_status(job_name, cluster_id, node_type, 4)

        # 12. Wait for client_stage to be 4
        listeners.wait_for_node_stage(job_name, cluster_id, node_type, 4)

        listeners.wait_for_aggregation_phase(job_name, cluster_id, node_type)

        # 13. Wait for process_stage to be 1 or 3
        process_stage = listeners.wait_for_start_end_training(
            job_name, cluster_id, node_type)

        # 14. If process_stage is 1, start again from step 7,
        #     else Update Client Status to 5 and exit
        if process_stage == 1:
            # update previous params and global round
            previous_param = curr_param
            global_round += 1

            start_time = time()

        if process_stage == 3:
            logger.info("Job [{job_name}] terminated. Exiting Process.")
            setters.update_node_status(job_name, cluster_id, node_type, 5)
            break
