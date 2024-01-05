'''
Gossip Peer Routing Module
'''
from flask import Blueprint, jsonify, request
# from state import peer_state
from apps.gossip.peer_management import PeerManager

ROUTE_NAME = 'gossip-peer'
ALIVE_THRESHOLD = 10
blueprint = Blueprint(ROUTE_NAME, __name__)

peer_manager = PeerManager()


@blueprint.route('/')
def root():
    '''
    blueprint root route, provides a brief description of the route,
    with some additional information.
    '''
    data = {'message': f'This is the \'{ROUTE_NAME}\' router.',
            'node_info': peer_manager.node_info()}
    return jsonify(data)


@blueprint.route('/node_info')
def node_info():
    '''
    route to get node information
    '''

    return jsonify(peer_manager.node_info())


@blueprint.route('/get_peers')
def get_peers():
    '''
    route to get all discovered nodes
    '''

    return jsonify(peer_manager.get_peers())


@blueprint.route('/get_alive_peers')
def get_alive_peers():
    '''
    route to get alive peers
    '''
    return jsonify(peer_manager.get_alive_peers())


@blueprint.route('/register_node', methods=['POST'])
def register_node():
    '''
    route to register node on current node
    '''
    req = request.get_json()
    node_id = req['node_id']
    node_data = req['node_info']

    # ip address of node which is used to discovery
    idis_ip = request.remote_addr

    peer_manager.register_node(node_id, node_data, idis_ip)

    return jsonify({'status': True}), 200


@blueprint.route('/alive_ping', methods=['POST'])
def alive_ping():
    '''
    send ping to notify node that sender is alive
    '''
    req = request.get_json()
    node_id = req['node_id']
    if peer_manager.alive_ping(node_id):
        return jsonify({'status': True}), 200
    else:
        return jsonify({'status': False}), 404
