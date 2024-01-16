'''
Module contianing logic to
1. Check for new jobs published on hte LogiCon Server
2. If node_id is mentioned a job, launch the client / worker process for the job+cluster
'''
from multiprocessing import Process
from state import jobs_proc_state
from helpers.argsparse import args
from helpers.logging import logger
from helpers.http import get
from apps.client import client_process
from apps.worker import worker_process


def get_jobs_from_server(logicon_url: str, job_set: set) -> None:
    '''
    Get job list from server
    '''

    url = f'{logicon_url}/job/list_jobs'

    jobs = get(url, {})

    # remove deleted jobs
    for job_id in list(job_set):
        if job_id not in jobs:
            # create the client and worker process ids
            client_proc = f'{job_id}#client'
            worker_proc = f'{job_id}#worker'

            # stop the client job process if running
            if client_proc in jobs_proc_state and jobs_proc_state[client_proc].is_alive():
                jobs_proc_state[client_proc].terminate()
                jobs_proc_state[client_proc].join()

                # remove the process from the proc_state
                del jobs_proc_state[client_proc]

            # stop the worker job process if running
            if worker_proc in jobs_proc_state and jobs_proc_state[worker_proc].is_alive():
                jobs_proc_state[worker_proc].terminate()
                jobs_proc_state[worker_proc].join()

                # remove the process from the proc_state
                del jobs_proc_state[worker_proc]

            # remove job process from jobs registry.
            job_set.remove(job_id)

    # add newly added jobs
    for job_id in jobs:
        if job_id not in job_set:
            if 'root' not in job_id:

                # add job ID to job set.
                job_set.add(job_id)

                # get the job manifest
                is_my_job = get_job_manifest(job_id, logicon_url)

                if not is_my_job:
                    job_set.remove(job_id)


def get_job_manifest(job_id: str, logicon_url: str) -> bool:
    '''
    Download job manifest from logicon for [job_id] and node_id
    '''
    is_my_job = False
    node_id = args['node_id']
    parts = job_id.split('#')
    job_name, cluster_id = parts[0], parts[1]

    url = f'{logicon_url}/job/get_participants'

    logger.info(f'Fetching Job Manifest for [{job_id}].')

    participants = get(url, {'job_name': job_name, 'cluster_id': cluster_id})[
        'payload']

    # if a particiapnt in client, spawn client process
    if node_id in participants['clients']:
        logger.info(f'Starting Client Process for Job [{job_id}]')

        proc_name = f'{job_id}#client'

        # start new job thread
        client_proc = Process(target=client_process,
                              args=(job_name, cluster_id),
                              name=proc_name, daemon=False)

        # start job process
        client_proc.start()

        jobs_proc_state[proc_name] = client_proc

        is_my_job = True

    # if a particiapnt in worker, spawn client process
    if node_id in participants['workers']:
        logger.info(f'Starting Worker Process for Job [{job_id}]')

        proc_name = f'{job_id}#worker'

        # start new job thread
        worker_proc = Process(target=worker_process,
                              args=(job_name, cluster_id),
                              name=proc_name, daemon=False)

        # start job process
        worker_proc.start()

        jobs_proc_state[proc_name] = worker_proc

        is_my_job = True

    return is_my_job
