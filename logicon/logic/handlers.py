'''
Auxuliary Scripts for Job Handling
'''
from logic.job import Job
from logic.consensus_exec import exec_consensus


def recursive_allow_jobsheet_download(job: Job) -> bool:
    '''
    Recursively allow job sheet download in any order
    '''

    status = job.allow_jobsheet_download()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_allow_jobsheet_download(sub_job)

    return status


def recursive_allow_dataset_download(job: Job) -> bool:
    '''
    Recursively allow dataset download in any order
    '''

    status = job.allow_dataset_download()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_allow_dataset_download(sub_job)

    return status


def recursive_abort_job(job: Job) -> bool:
    '''
    Recursively abort a job collection in any order
    '''

    status = job.set_abort()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_abort_job(sub_job)

    return status


def recursive_terminate_job(job: Job) -> bool:
    '''
    Recursively abort a job collection in any order
    '''

    status = job.terminate_training()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_terminate_job(sub_job)

    return status


def recursive_check_delete_job(job: Job) -> bool:
    '''
    Recursively check if a job collection can be delete (in any order)
    '''

    status = job.job_status['process_stage'] == 3

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_check_delete_job(sub_job)

    return status


def recursive_client_status_handler(job: Job, client_id: str, client_status: str) -> bool:
    '''
    Recursively handle side-effects of client status update
    '''

    status, side_effect = job.update_client_status(client_id, client_status)

    if side_effect == 101:
        # send job download ack to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'])

        # set download flag true (allow dataset download)
        status = status and job.allow_dataset_download()

    if side_effect == 102:
        # send dataset download ack to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'])

        # set process_phase to 1 (allow start training)
        # but before that set the initial global params
        status = status and job.set_global_model_param(
            job.exec_params['initial_params'][0], dict())
        status = status and job.allow_start_training()

    if side_effect == 201:
        # update client / cluster status to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'])

    return status


def recursive_worker_status_handler(job: Job, worker_id: str, worker_status: str) -> bool:
    '''
    Recursively handle side-effects of client status update
    '''

    status, side_effect = job.update_worker_status(worker_id, worker_status)

    if side_effect == 101:
        # send job download ack to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'])

        # set download flag true (allow dataset download)
        status = status and job.allow_dataset_download()

    if side_effect == 102:
        # send dataset download ack to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, job.cluster_id, job.job_status['client_stage'])

        # set process_phase to 1 (allow start training)
        # but before that set the initial global params
        status = status and job.set_global_model_param(
            job.exec_params['initial_params'][0], dict())
        status = status and job.allow_start_training()

    if side_effect == 301:
        # execute the consensus to select global update param
        exec_status, global_param, global_extra_data = exec_consensus(job)

        status = status and exec_status

        # update process_phase (or) continue training (or) upload global update to upstream cluster
        # refer to last stage of point 7, in docs/workflow.md
        if job.is_primary:
            status = status and recursive_set_global_params_and_start_training(
                job, global_param, global_extra_data)
        else:
            # if the current cluster epoch is the final epoch
            if job.is_final_cluster_epoch():
                # upload global param to upstream job and update client / cluster status
                upstream_job = Job(job.job_name, job.cluster_id,
                                   {}, {}, {}, load_from_db=True)

                status = status and upstream_job.append_client_params(
                    job.cluster_id, global_param, global_extra_data)

                status = status and recursive_client_status_handler(
                    upstream_job, job.cluster_id, job.job_status['client_stage'])

                # reset the current cluster epoch to 1
                job.reset_cluster_epoch()
            else:
                # resume training and increment epoch by 1
                job.increment_cluster_epoch()
                status = status and recursive_set_global_params_and_start_training(
                    job, global_param, global_extra_data)

    return status


def recursive_set_global_params_and_start_training(job: Job, param: str, extra_data: str) -> bool:
    '''
    Recursively set the global params for the job in all clusters and 
    set process_stage to 1.
    from root to leaf
    '''
    status = job.set_global_model_param(param, extra_data)

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_set_global_params_and_start_training(
            sub_job, param, extra_data)

    status = status and job.allow_start_training()

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