'''
The Client Process Module
'''
from env import env
from helpers.argsparse import args


def client_process(job_name: str, cluster_id: str) -> None:
    '''
    Client Process
    1. Download Job Configuration
    2. ACK of Job Sheet Download (Client Status to 1)
    3. Wait for DatasetDownload Flag
    4. Download the Dataset
        1. Preprocess Dataset
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
    logicon_url = env['LOGICON_URL']
