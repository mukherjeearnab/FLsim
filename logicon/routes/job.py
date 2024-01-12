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

        return jsonify({'message': 'Job instance created successfully!', 'status': True}), 200
    except Exception:
        logger.error(
            f'Failed to Create Job Instance.\n{traceback.format_exc()}')
        return jsonify({'message': 'Failed to create job  instance!', 'status': False}), 500


@blueprint.route('/append_client_params', methods=['POST'])
def append_client_params():
    # TODO

@blueprint.route('/append_worker_params', methods=['POST'])
def append_worker_params():
    # TODO

@blueprint.route('/update_client_status', methods=['POST'])
def update_client_status():
    # TODO

@blueprint.route('/update_worker_status', methods=['POST'])
def update_worker_status():
    # TODO

@blueprint.route('/set_abort', methods=['POST'])
def set_abort():
    # TODO

@blueprint.route('/terminate_training', methods=['POST'])
def terminate_training():
    # TODO