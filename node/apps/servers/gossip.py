'''
The Gossip Server Module
'''
import random
from multiprocessing import Process
from flask import Flask, jsonify
# from state import peer_state
from helpers.argsparse import args
from helpers.networking import check_local_port_bind
from apps.gossip.peer_management import PeerManager
from routes.peer import blueprint as peer_management
# from routes.job_manager import blueprint as job_manager

peer_manager = PeerManager()

# import the routers for different routes

app = Flask(__name__)


@app.route('/')
def root():
    '''
    server root route, provides a brief description of the server,
    with some additional information.
    '''
    data = {'message': 'This is the gossip server endpoint.'}
    return jsonify(data)


# register the blueprint routes
app.register_blueprint(peer_management, url_prefix='/peer')
# app.register_blueprint(job_manager, url_prefix='/job_manager')


def run_server():
    '''
    Method to create a thread for the server process
    '''
    if args['random_gossip_port']:
        port = random.randint(10000, 20000)
    else:
        if check_local_port_bind(args['gossip_port']):
            port = args['gossip_port']
        else:
            port = random.randint(10000, 20000)

    peer_manager.set_gossip_port(port)

    print(f'Gossip server listening on port {port}.')
    app.run(port=port, debug=False,
            threaded=True, host='0.0.0.0')


server = Process(target=run_server, name="gossip_server_process", daemon=True)


def start_server():
    '''
    Method to start the server
    '''
    server.start()
    print('Gossip server started.')


def stop_server():
    '''
    Method to stop the server, it joins it, and then exit will be called
    '''
    print('Stopping Gossip server...')
    if server.is_alive():
        server.terminate()
        server.join()
