'''
Auxuliary Scripts for Job Handling
'''
import threading
from typing import Dict
from logic.job import Job
from logic.consensus_exec import exec_consensus


def recursive_allow_jobsheet_download(job: Job, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively allow job sheet download in any order
    '''

    status = job.allow_jobsheet_download()

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_allow_jobsheet_download(
            sub_job, job_locks) and status

    return status


def recursive_allow_dataset_download(job: Job, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively allow dataset download in any order
    '''

    status = job.allow_dataset_download()

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_allow_dataset_download(
            sub_job, job_locks) and status

    return status


def recursive_abort_job(job: Job, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively abort a job collection in any order
    '''

    status = job.set_abort()

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_abort_job(sub_job, job_locks) and status

    return status


def recursive_terminate_job(job: Job, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively abort a job collection in any order
    '''

    status = job.terminate_training()

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_terminate_job(sub_job, job_locks) and status

    return status


def recursive_check_delete_job(job: Job, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively check if a job collection can be delete (in any order)
    '''

    status = job.job_status['process_stage'] == 3

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_check_delete_job(sub_job, job_locks) and status

    return status


def recursive_client_status_handler(job: Job, client_id: str, client_status: str,  job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively handle side-effects of client status update
    '''

    status, side_effect = job.update_client_status(client_id, client_status)

    if side_effect == 101:
        # send job download ack to upstream cluster
        if not job.is_primary:
            job_id = f'{job.job_name}#{job.cluster_config["upstream_cluster"]}'
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)
            status = recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

        # set download flag true (allow dataset download)
        status = job.allow_dataset_download() and status

    if side_effect == 102:
        # send dataset download ack to upstream cluster
        if not job.is_primary:
            job_id = f'{job.job_name}#{job.cluster_config["upstream_cluster"]}'
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)
            status = recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

        # set process_phase to 1 (allow start training)
        # but before that set the initial global params
        status = job.set_global_model_param(
            job.exec_params['initial_params'][0], 'empty') and status
        status = job.allow_start_training() and status

    if side_effect == 201:
        # update client / cluster status to upstream cluster
        if not job.is_primary:
            job_id = f'{job.job_name}#{job.cluster_config["upstream_cluster"]}'
            print(f'EXEC SE 201 {job_id}')
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)
            status = recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

    return status


def recursive_worker_status_handler(job: Job, worker_id: str, worker_status: str, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively handle side-effects of client status update
    '''

    status, side_effect = job.update_worker_status(worker_id, worker_status)

    if side_effect == 101:
        # send job download ack to upstream cluster
        if not job.is_primary:
            job_id = f'{job.job_name}#{job.cluster_config["upstream_cluster"]}'
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)
            status = recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

        # set download flag true (allow dataset download)
        status = job.allow_dataset_download() and status

    if side_effect == 102:
        # send dataset download ack to upstream cluster
        if not job.is_primary:
            job_id = f'{job.job_name}#{job.cluster_config["upstream_cluster"]}'
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)
            status = recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

        # set process_phase to 1 (allow start training)
        # but before that set the initial global params
        status = job.set_global_model_param(
            job.exec_params['initial_params'][0], 'empty') and status
        status = job.allow_start_training() and status

    if side_effect == 301:
        # execute the consensus to select global update param
        exec_status, global_param, global_extra_data = exec_consensus(job)

        status = exec_status and status

        # update process_phase (or) continue training (or) upload global update to upstream cluster
        # refer to last stage of point 7, in docs/workflow.md
        if job.is_primary:
            print(F'EXEC 301 PRIMARY {job.job_name}#{job.cluster_id}')
            status = recursive_set_global_params_and_start_training(
                job, global_param, global_extra_data, job_locks) and status
        else:
            # if the current cluster epoch is the final epoch
            if job.is_final_cluster_epoch():
                print(F'EXEC 301 FINE {job.job_name}#{job.cluster_id}')
                # upload global param to upstream job and update client / cluster status
                job_id = f'{job.job_name}#{job.cluster_id}'
                upstream_job = Job(
                    job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, job_locks[job_id], load_from_db=True)

                status = upstream_job.append_client_params(
                    job.cluster_id, global_param, global_extra_data) and status

                status = recursive_client_status_handler(
                    upstream_job, job.cluster_id, job.job_status['client_stage'], job_locks) and status

                # reset the current cluster epoch to 1
                job.reset_cluster_epoch()
            else:
                print(F'EXEC 301 NONFE {job.job_name}#{job.cluster_id}')
                # resume training and increment epoch by 1
                job.increment_cluster_epoch()
                status = recursive_set_global_params_and_start_training(
                    job, global_param, global_extra_data, job_locks) and status

    return status


def recursive_set_global_params_and_start_training(job: Job, param: str, extra_data: str, job_locks: Dict[str, threading.Lock]) -> bool:
    '''
    Recursively set the global params for the job in all clusters and 
    set process_stage to 1.
    from root to leaf
    '''
    print('REC_SETTING_GLOBAL_PARAM', job.cluster_id)
    status = job.set_global_model_param(param, extra_data)

    for cluster_id in job.sub_clusters:
        job_id = f'{job.job_name}#{cluster_id}'
        print('REC_SET_GLOBAL_PARAM', job_id)
        sub_job = Job(job.job_name, cluster_id, {}, {}, {},
                      job_locks[job_id], load_from_db=True)
        status = recursive_set_global_params_and_start_training(
            sub_job, param, extra_data, job_locks) and status

    status = job.allow_start_training() and status

    return status


def append_initial_params(job: Job, node_id: str, param: str) -> bool:
    '''
    Wrapper function to append initial parameters to job
    '''
    status = job.append_initial_params(node_id, param)

    return status


def get_config(job: Job, config_type: str) -> bool:
    '''
    Wrapper function to get job config
    '''
    return job.get_config(config_type)


def get_participants(job: Job) -> bool:
    '''
    Wrapper function to get job participants
    '''
    return job.get_participants()


def get_job_status(job: Job) -> bool:
    '''
    Wrapper function to get job status
    '''
    return job.get_job_status()


def get_exec_params(job: Job) -> bool:
    '''
    Wrapper function to get job exec_params
    '''
    return job.get_exec_params()
