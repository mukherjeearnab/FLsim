'''
The Client Process Module
'''
import traceback
from copy import deepcopy
from helpers.argsparse import args
from helpers.logging import logger
from helpers.converters import get_base64_state_dict
from apps.client import listeners, handlers
from apps.common import getters, setters


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

    # 0. Wait for JobsheetDownload Flag
    listeners.wait_for_jobsheet_flag(job_name, cluster_id)

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
    previous_params = get_base64_state_dict(prev_local_model)

    # 3. Wait for DatasetDownload Flag
    listeners.wait_for_dataset_flag(job_name, cluster_id)

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

    # 5. ACK of Dataset Download (Client Status to 2) & Send Back Initial Model (Global) Parameters
    # upload init_params to p2p store and obtain the init_params_key
    setters.update_node_status(
        job_name, cluster_id, node_type, 2, {'initial_param': init_params_key})
