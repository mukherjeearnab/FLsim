'''
Key Value Store Management Router
'''
import os
import threading
from dotenv import load_dotenv
from waitress import serve
from flask import Flask, jsonify, request
from perflog import PerformanceLog

# import environment variables
load_dotenv()

app = Flask(__name__)

WRITE_LOCK = threading.Lock()
LISTEN_PORT = int(os.getenv('LISTEN_PORT'))

PROJECTS = {}


@app.route('/')
def root():
    '''
    app root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': 'This is the Performance Logger Microservice.'}
    return jsonify(data)


@app.route('/init_project', methods=['POST'])
def init_project():
    '''
    Initialize the project
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    config = payload['config']

    # WRITE_LOCK.wait()

    project = PerformanceLog(job_name, config)
    PROJECTS[job_name] = project

    return jsonify({'message': f'Project Init [{job_name}]', 'res': 200})


@app.route('/add_record', methods=['POST'])
def add_record():
    '''
    Add a metrics record.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    cluster_id = payload['cluster_id']
    node_id = payload['node_id']
    node_type = payload['node_type']
    round_num = payload['round_num']
    epoch_num = payload['epoch_num']
    metrics = payload['metrics']
    time_delta = payload['time_delta']

    WRITE_LOCK.acquire()

    PROJECTS[job_name].add_perflog(
        cluster_id, node_id, node_type, round_num, epoch_num, metrics, time_delta)

    WRITE_LOCK.release()
    return jsonify({'res': 200})


@app.route('/add_params', methods=['POST'])
def add_params():
    '''
    Add Model Params record.
    '''
    payload = request.get_json()

    job_name = payload['job_name']
    params = payload['params']
    round_num = payload['round_num']

    WRITE_LOCK.acquire()

    PROJECTS[job_name].save_params(round_num, params)

    WRITE_LOCK.release()
    return jsonify({'res': 200})


@app.route('/save_logs', methods=['POST'])
def save_logs():
    '''
    Save all records.
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    WRITE_LOCK.acquire()

    PROJECTS[job_name].save()

    WRITE_LOCK.release()
    return jsonify({'res': 200})


@app.route('/terminate', methods=['POST'])
def terminate():
    '''
    Job Logging Termination.
    '''
    payload = request.get_json()

    job_name = payload['job_name']

    WRITE_LOCK.acquire()

    PROJECTS[job_name].terminate_resource_logger()

    WRITE_LOCK.release()
    return jsonify({'res': 200})


if __name__ == '__main__':
    app.run(port=LISTEN_PORT, debug=False, host='0.0.0.0')
    # serve(app, host="0.0.0.0", port=LISTEN_PORT)
