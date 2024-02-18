'''
Key Value Store Management Router
'''
import sys
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


@app.route('/size')
def get_size():
    '''
    get the size of the kvstore object
    '''

    def get_size(obj, seen=None):
        """Recursively finds size of objects"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([get_size(v, seen) for v in obj.values()])
            size += sum([get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([get_size(i, seen) for i in obj])
        return size

    try:
        kv_size = get_size(keyValueStore.table)
        return jsonify({'status': True, 'size': kv_size}), 200
    except:
        return jsonify({'status': False, 'size': -1}), 500



if __name__ == '__main__':
    app.run(port=6666, debug=False, host='0.0.0.0')
