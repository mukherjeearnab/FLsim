'''
Key Value Store Management Router
'''

from flask import Flask, jsonify, request
from key_val_store import KeyValueStore

app = Flask(__name__)


keyValueStore = KeyValueStore()


@app.route('/')
def root():
    '''
    app root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': 'This is the Key Value Store Microservice.'}
    return jsonify(data)


@app.route('/get')
def get_val():
    '''
    get value of key
    '''

    key = request.args['key']

    value, status = keyValueStore.get(key)

    return jsonify({'status': status, 'value': value}), 200 if status else 404


@app.route('/delete')
def delete_val():
    '''
    get value of key
    '''

    key = request.args['key']

    value, status = keyValueStore.delete(key)

    return jsonify({'status': status, 'value': value}), 200 if status else 404


@app.route('/set', methods=['POST'])
def set_val():
    '''
    register route, for clients to register on the server and obtain IDs.
    '''
    data = request.get_json()
    value = data['value']

    try:
        key = keyValueStore.set(value)
        return jsonify({'status': True, 'key': key}), 200
    except:
        return jsonify({'status': False, 'key': None}), 500


if __name__ == '__main__':
    app.run(port=6666, debug=False, host='0.0.0.0')
