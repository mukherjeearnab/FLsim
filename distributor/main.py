'''
Key Value Store Management Router
'''
from flask import Flask, jsonify, request, send_file
from logic import DatasetDistributor
from helpers.file import get_OK_file

app = Flask(__name__)


datasetDistributor = DatasetDistributor()


@app.route('/')
def root():
    '''
    app root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': 'This is Dataset Distributor Microservice.'}
    return jsonify(data)


@app.route('/delete')
def delete():
    '''
    Delete Dataset Config for Job
    '''
    job_name = request.args['job_name']

    status = datasetDistributor.delete_job(job_name)

    return jsonify({'status': status}), 200 if status else 500


@app.route('/prepare', methods=['POST'])
def prepare():
    '''
    Prepare dataset chunks for clients to download
    '''
    req = request.get_json()
    job_name = req['job_name']
    manifest = req['manifest']

    status, message = datasetDistributor.register_n_prepare(job_name, manifest)
    metadata = datasetDistributor.get_dataset_metadata(
        job_name, None, 'complete')

    return jsonify({'status': status, 'message': message, 'metadata': metadata}), 200 if status else 500


@app.route('/download_dataset')
def download_dataset():
    '''
    ROUTE to download dataset, based on client_id and job_name
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']
    client_id = request.args['client_id']

    res = datasetDistributor.get_dataset_metadata(
        job_name, cluster_id, client_id)
    if res is not None:
        return send_file(res, mimetype='application/octet-stream',
                         download_name=res.split('/')[-1], as_attachment=True)
    else:
        return jsonify({'message': f'Dataset File for Job [{job_name}], Cluster [{cluster_id}], Client [{client_id}] not found!'}), 404


@app.route('/get_dataset_metadata')
def get_dataset_metadata():
    '''
    ROUTE to get dataset version timestamp, based on client_id and job_name
    '''
    job_name = request.args['job_name']
    cluster_id = request.args['cluster_id']
    client_id = request.args['client_id'] if 'client_id' in request.args else None

    ok_file = datasetDistributor.get_dataset_metadata(
        job_name, cluster_id, 'ok_file')

    weights = datasetDistributor.get_dataset_metadata(
        job_name, cluster_id, 'weights')

    if client_id is not None:
        dataset_file = datasetDistributor.get_dataset_metadata(
            job_name, cluster_id, client_id)
    else:
        dataset_file = None

    if ok_file is not None:
        timestamp = get_OK_file(ok_file)
        return jsonify({'timestamp': timestamp, 'path': ok_file, 'file': dataset_file, 'weights': weights}), 200
    else:
        return jsonify({'message': f'Metadata for Job [{job_name}], Cluster [{cluster_id}] not found!'}), 404


if __name__ == '__main__':
    app.run(port=8888, debug=False, host='0.0.0.0')
