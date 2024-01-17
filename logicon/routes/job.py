'''
Client Management Routing Module
'''
import threading
import traceback
from flask import Blueprint, jsonify, request
from state import job_route_state
from helpers.logging import logger
from logic.job import Job
from logic import handlers


ROUTE_NAME = 'job-manager'
blueprint = Blueprint(ROUTE_NAME, __name__)
job_locks = dict()


@blueprint.route('/')
def root():
    '''
    blueprint root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': f'This is the \'{ROUTE_NAME}\' router.'}
    return jsonify(data)


@blueprint.route('/list_jobs')
def list_jobs():
    '''
    returns the list of all the jobs present in the system
    '''

    jobs = list(job_route_state.keys())
    jobs = list(filter(lambda job: 'root' not in job, jobs))

    return jsonify(jobs)


@blueprint.route('/get_config')
def get_config():
    '''
    get job config
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']
    config_type = request.args['config_type']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'payload': None, 'status': False}), 404

    try:
        job = job_route_state[job_id]
        payload = handlers.get_config(job, config_type)

        if payload is None:
            return jsonify({'message': 'Malformed config_type.', 'payload': payload, 'status': False}), 403

        return jsonify({'message': 'Fetch successful!', 'payload': payload, 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Fetch Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to fetch job config!', 'payload': None, 'status': False}), 500


@blueprint.route('/get_participants')
def get_participants():
    '''
    get job config
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'payload': None, 'status': False}), 404

    try:
        job = job_route_state[job_id]
        payload = handlers.get_participants(job)

        if payload is None:
            raise Exception('Job does not exist in job state variable')

        return jsonify({'message': 'Fetch successful!', 'payload': payload, 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Fetch Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to fetch job participants!', 'payload': None, 'status': False}), 500


@blueprint.route('/get_job_status')
def get_job_status():
    '''
    get job config
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'payload': None, 'status': False}), 404

    try:
        job = job_route_state[job_id]
        payload = handlers.get_job_status(job)

        if payload is None:
            raise Exception('Job does not exist in job state variable')

        return jsonify({'message': 'Fetch successful!', 'payload': payload, 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Fetch Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to fetch job status!', 'payload': None, 'status': False}), 500


@blueprint.route('/get_exec_params')
def get_exec_params():
    '''
    get job config
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'payload': None, 'status': False}), 404

    try:
        job = job_route_state[job_id]
        payload = handlers.get_exec_params(job)

        if payload is None:
            raise Exception('Job does not exist in job state variable')

        return jsonify({'message': 'Fetch successful!', 'payload': payload, 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Fetch Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to fetch job exec_params!', 'payload': None, 'status': False}), 500


@blueprint.route('/create', methods=['POST'])
def create_job_route():
    '''
    initialize the jobs for clusters
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    job_manifest = payload['manifest']

    if job_name in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] already exists.', 'status': False}), 403

    try:
        for cluster_id in job_manifest['clusters'].keys():
            job_id = f'{job_name}#{cluster_id}'

            # create the job lock
            job_locks[job_id] = threading.Lock()

            # create the job_object
            job = Job(job_name, cluster_id,
                      job_manifest['clients'], job_manifest['workers'], job_manifest['clusters'], job_locks[job_id])

            if job.is_primary:
                job_route_state[f'{job_name}#root'] = job
            job_route_state[job_id] = job

            logger.info(f'Created job {job_id}')

        return jsonify({'message': 'Job instance created successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Create Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to create job instance!', 'status': False}), 500


@blueprint.route('/start', methods=['POST'])
def start_job_route():
    '''
    start the job for clusters
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    root_job_name = f'{job_name}#root'

    if root_job_name not in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] does not exist.', 'status': False}), 404

    try:
        root_job = job_route_state[root_job_name]
        status = handlers.recursive_allow_jobsheet_download(
            root_job, job_locks)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance started successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Start Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to start job instance!', 'status': False}), 500


@blueprint.route('/append_client_params', methods=['POST'])
def append_client_params():
    '''
    Append Trained Client Params to Job Instance of a cluster.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    cluster_id = payload['cluster_id']
    client_id = payload['client_id']
    param = payload['param']
    extra_data = payload['extra_data']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'status': False}), 404

    try:
        job = job_route_state[job_id]
        status = job.append_client_params(client_id, param, extra_data)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Client param appended successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to append client params.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to append client params!', 'status': False}), 500


@blueprint.route('/append_worker_params', methods=['POST'])
def append_worker_params():
    '''
    Append Aggregated Worker Params to Job Instance of a cluster.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    cluster_id = payload['cluster_id']
    worker_id = payload['worker_id']
    param = payload['param']
    extra_data = payload['extra_data']

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'status': False}), 404

    try:
        job = job_route_state[job_id]
        status = job.append_worker_params(worker_id, param, extra_data)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Worker param appended successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to append worker params.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to append worker params!', 'status': False}), 500


@blueprint.route('/update_client_status', methods=['POST'])
def update_client_status():
    '''
    Update Client Status to Job Instance of a cluster.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    cluster_id = payload['cluster_id']
    client_id = payload['client_id']
    client_status = payload['status']
    extra_data = payload['extra_data'] if payload['extra_data'] is not None else None

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'status': False}), 404

    status = True

    try:
        leaf_job = job_route_state[job_id]

        # special case: when client status is 2,
        # they also submit the initial global parameters, append it.
        if extra_data is not None and 'initial_param' in extra_data:
            status = status and handlers.append_initial_params(
                leaf_job, client_id, extra_data['initial_param'])

        status = status and handlers.recursive_client_status_handler(
            leaf_job, client_id, client_status, job_locks)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Client status updated successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to update client status.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to update client status!', 'status': False}), 500


@blueprint.route('/update_worker_status', methods=['POST'])
def update_worker_status():
    '''
    Update Worker Status to Job Instance of a cluster.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    cluster_id = payload['cluster_id']
    worker_id = payload['worker_id']
    worker_status = payload['status']
    extra_data = payload['extra_data'] if payload['extra_data'] is not None else None

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'status': False}), 404

    status = True

    try:
        leaf_job = job_route_state[job_id]

        # special case: when worker status is 2,
        # they also submit the initial global parameters, append it.
        if extra_data is not None and 'initial_param' in extra_data:
            status = status and handlers.append_initial_params(
                leaf_job, worker_id, extra_data['initial_param'])

        status = status and handlers.recursive_worker_status_handler(
            leaf_job, worker_id, worker_status, job_locks)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Worker status updated successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to update worker status.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to update worker status!', 'status': False}), 500


@blueprint.route('/set_abort', methods=['POST'])
def set_abort():
    '''
    Abort a running job instance
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    root_job_name = f'{job_name}#root'

    if root_job_name not in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] does not exist.', 'status': False}), 404

    try:
        root_job = job_route_state[root_job_name]
        status = handlers.recursive_abort_job(root_job, job_locks)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance aborted successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Abort Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to abort job instance!', 'status': False}), 500


@blueprint.route('/terminate_training', methods=['POST'])
def terminate_training():
    '''
    Terminate a running job instance
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    root_job_name = f'{job_name}#root'

    if root_job_name not in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] does not exist.', 'status': False}), 404

    try:
        root_job = job_route_state[root_job_name]
        status = handlers.recursive_terminate_job(root_job, job_locks)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance terminated successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Terminate Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to terminate job instance!', 'status': False}), 500


@blueprint.route('/delete', methods=['POST'])
def delete_job():
    '''
    Delete a terminated job instance
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    root_job_name = f'{job_name}#root'

    if root_job_name not in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] does not exist.', 'status': False}), 404

    try:
        root_job = job_route_state[root_job_name]
        can_delete = handlers.recursive_check_delete_job(root_job, job_locks)

        if can_delete:
            for job_id in list(job_route_state.keys()):
                if job_name == job_id.split('#')[0]:
                    del job_route_state[job_id]

        if not can_delete:
            return jsonify({'message': 'Error! Jobs are not terminated.', 'status': False}), 403

        return jsonify({'message': 'Job instance deleted successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Delete Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to delete job instance!', 'status': False}), 500
