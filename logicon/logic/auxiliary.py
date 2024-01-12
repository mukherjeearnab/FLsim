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
