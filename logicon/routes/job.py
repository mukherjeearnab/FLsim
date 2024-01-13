'''
Client Management Routing Module
'''
import threading
import traceback
from flask import Blueprint, jsonify, request
from state import job_route_state
from helpers.logging import logger
from logic.job import Job
from logic import auxiliary


ROUTE_NAME = 'job-manager'
blueprint = Blueprint(ROUTE_NAME, __name__)


@blueprint.route('/')
def root():
    '''
    blueprint root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': f'This is the \'{ROUTE_NAME}\' router.'}
    return jsonify(data)

# TODO: implement get functions
# TODO: implement list jobs and delete job functions

@blueprint.route('/create', methods=['POST'])
def create_job_route():
    '''
    initialize the jobs for clusters
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    job_manifest = request.args['manifest']

    if job_name in job_route_state:
        return jsonify({'message': f'Job with name [{job_name}] already exists.', 'status': False}), 403

    try:
        for cluster_id in job_manifest['clusters'].keys():
            job = Job(job_name, cluster_id,
                      job_manifest['clients'], job_manifest['workers'], job_manifest['clusters'])
            if job.is_primary:
                job_route_state[f'{job_name}#root'] = job
            job_route_state[f'{job_name}#{cluster_id}'] = job

        return jsonify({'message': 'Job instance created successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Create Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to create job  instance!', 'status': False}), 500


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
        status = auxiliary.recursive_allow_jobsheet_download(root_job)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance started successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Start Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to start job  instance!', 'status': False}), 500


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
        logger.error( f'Failed to append client params.\n{traceback.format_exc()}')
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
        logger.error( f'Failed to append worker params.\n{traceback.format_exc()}')
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

    job_id = f'{job_name}#{cluster_id}'

    if job_id not in job_route_state:
        return jsonify({'message': f'Job [{job_name}] for Cluster [{cluster_id}] does not exist.', 'status': False}), 404
    
    try:
        leaf_job = job_route_state[job_id]
        status = auxiliary.recursive_client_status_handler(leaf_job, client_id, client_status)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403
        
        return jsonify({'message': 'Client status updated successfully!', 'status': True}), 200
    except Exception:
        logger.error( f'Failed to update client status.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to update client status!', 'status': False}), 500

@blueprint.route('/update_worker_status', methods=['POST'])
def update_worker_status():
    # TODO

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
        status = auxiliary.recursive_abort_job(root_job)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance aborted successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Abort Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to abort job  instance!', 'status': False}), 500

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
        status = auxiliary.recursive_terminate_job(root_job)

        if not status:
            return jsonify({'message': 'Failure in compliance with Job Logic.', 'status': False}), 403

        return jsonify({'message': 'Job instance terminated successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Terminate Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to terminate job  instance!', 'status': False}), 500
