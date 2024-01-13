'''
Auxuliary Scripts for Job Handling
'''
from logic.job import Job


def recursive_allow_jobsheet_download(job: Job):
    '''
    Recursively allow job sheet download in any order
    '''

    status = job.allow_jobsheet_download()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_allow_jobsheet_download(sub_job)

    return status


def recursive_allow_dataset_download(job: Job):
    '''
    Recursively allow dataset download in any order
    '''

    status = job.allow_dataset_download()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_allow_dataset_download(sub_job)

    return status


def recursive_abort_job(job: Job):
    '''
    Recursively abort a job collection in any order
    '''

    status = job.set_abort()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_abort_job(sub_job)

    return status


def recursive_terminate_job(job: Job):
    '''
    Recursively abort a job collection in any order
    '''

    status = job.terminate_training()

    for cluster_id in job.sub_clusters():
        sub_job = Job(job.job_name, cluster_id, {}, {}, {}, load_from_db=True)
        status = status and recursive_terminate_job(sub_job)

    return status


def recursive_client_status_handler(job: Job, client_id: str, client_status: str):
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
                upstream_job, client_id, job.job_status['client_stage'])

        # set download flag true (allow dataset download)
        job.allow_dataset_download()

    if side_effect == 102:
        # send dataset download ack to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, client_id, job.job_status['client_stage'])

        # set process_phase to 1 (allow start training)
        # TODO: ALSO SET GLOBAL PARAMS (recursive, root to leaf)
        job.allow_start_training()

    if side_effect == 201:
        # update client / cluster status to upstream cluster
        if not job.is_primary:
            upstream_job = Job(
                job.job_name, job.cluster_config['upstream_cluster'], {}, {}, {}, load_from_db=True)
            status = status and recursive_client_status_handler(
                upstream_job, client_id, job.job_status['client_stage'])

    return status
