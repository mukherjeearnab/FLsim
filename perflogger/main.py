'''
Key Value Store Management Router
'''
import threading
from flask import Flask, jsonify, request
from perflog import PerformanceLog

app = Flask(__name__)

WRITE_LOCK = threading.Lock()

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

    job_id = payload['job_id']
    config = payload['config']

    # WRITE_LOCK.wait()

    project = PerformanceLog(job_id, config)
    PROJECTS[job_id] = project

    return jsonify({'message': f'Project Init [{job_id}]', 'res': 200})


@app.route('/add_record', methods=['POST'])
def add_record():
    '''
    Add a metrics record.
    '''
    payload = request.get_json()

    client_id = payload['client_id']
    round_num = payload['round_num']
    job_id = payload['job_id']
    metrics = payload['metrics']
    time_delta = payload['time_delta']

    WRITE_LOCK.acquire()

    PROJECTS[job_id].add_perflog(client_id, round_num, metrics, time_delta)

    WRITE_LOCK.release()
    return jsonify({'res': 200})


@app.route('/add_params', methods=['POST'])
def add_params():
    '''
    Add Model Params record.
    '''
    payload = request.get_json()

    job_id = payload['job_id']
    params = payload['params']
    round_num = payload['round_num']

    WRITE_LOCK.acquire()

    PROJECTS[job_id].save_params(round_num, params)

    WRITE_LOCK.release()
    return jsonify({'res': 200})


@app.route('/save_logs', methods=['POST'])
def save_logs():
    '''
    Save all records.
    '''
    payload = request.get_json()

    job_id = payload['job_id']

    WRITE_LOCK.acquire()

    PROJECTS[job_id].save()

    WRITE_LOCK.release()
    return jsonify({'res': 200})


if __name__ == '__main__':
    app.run(port=7777, debug=False, host='0.0.0.0')
