'''
Key Value Store Management Router
'''
from flask import Flask, jsonify, request


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


@app.route('/prepare', methods=['POST'])
def prepare():
    '''
    Prepare dataset chunks for clients to download
    '''

    return jsonify({'status': status, 'value': value}), 200 if status else 404


@app.route('/download_dataset')
def download_dataset():
    '''
    ROUTE to download dataset, based on client_id and job_name
    '''
    client_id = request.args['client_id']
    job_id = request.args['job_id']
    status = 200

    if job_id in JOBS:
        CHUNK_DIR_NAME = 'dist'

        if JOBS[job_id][0].hierarchical:
            client_split_key = 'splits'
        else:
            client_split_key = 'clients'

        for chunk in JOBS[job_id][0].client_params['dataset']['distribution'][client_split_key]:
            CHUNK_DIR_NAME += f'-{chunk}'

        DATASET_PREP_MOD = JOBS[job_id][0].dataset_params['prep']['file']
        DATASET_DIST_MOD = JOBS[job_id][0].client_params['dataset']['distribution']['distributor']['file']
        DATASET_CHUNK_PATH = f"../../datasets/deploy/{DATASET_PREP_MOD}/chunks/{DATASET_DIST_MOD}/{CHUNK_DIR_NAME}"

        chunk_id = 0
        for i, client in enumerate(JOBS[job_id][0].job_status['client_info']):
            if client['client_id'] == client_id:
                chunk_id = i

        file_name = f'{chunk_id}.tuple'
        file_path = f'{DATASET_CHUNK_PATH}/{file_name}'

        return send_file(file_path, mimetype='application/octet-stream',
                         download_name=file_name, as_attachment=True)
    else:
        status = 404
        return jsonify({'message': f'Dataset File for Client [{client_id}] not found for Job [{job_id}]!'}), status


@app.route('/get_dataset_metadata')
def get_dataset_metadata():
    '''
    ROUTE to get dataset version timestamp, based on client_id and job_name
    '''
    job_id = request.args['job_id']
    status = 200

    if job_id in JOBS:
        CHUNK_DIR_NAME = 'dist'

        if JOBS[job_id][0].hierarchical:
            client_split_key = 'splits'
        else:
            client_split_key = 'clients'

        for chunk in JOBS[job_id][0].client_params['dataset']['distribution'][client_split_key]:
            CHUNK_DIR_NAME += f'-{chunk}'

        DATASET_PREP_MOD = JOBS[job_id][0].dataset_params['prep']['file']
        DATASET_DIST_MOD = JOBS[job_id][0].client_params['dataset']['distribution']['distributor']['file']
        DATASET_CHUNK_PATH = f"../../datasets/deploy/{DATASET_PREP_MOD}/chunks/{DATASET_DIST_MOD}/{CHUNK_DIR_NAME}"

        dataset_path = DATASET_CHUNK_PATH.replace('../../datasets/deploy/', '')
        file_path = f'./datasets/deploy/{dataset_path}/OK'
        with open(file_path, 'r', encoding='utf8') as f:
            content = f.read()

        return jsonify({'timestamp': content, 'path': dataset_path})
    else:
        status = 404
        return jsonify({'message': f'Job not found for Job [{job_id}]!'}), status


if __name__ == '__main__':
    app.run(port=6666, debug=False, host='0.0.0.0')
