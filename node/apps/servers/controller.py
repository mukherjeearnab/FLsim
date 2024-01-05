'''
The Controller Module
'''
from multiprocessing import Process
from flask import Flask, jsonify
from helpers.argsparse import args
from helpers.networking import check_local_port_bind
# from state import peer_state
from apps.gossip.peer_management import PeerManager
# from routes.client_manager import blueprint as client_manager
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
    data = {'message': 'This is the controller server endpoint.'}
    return jsonify(data)


# register the blueprint routes
# app.register_blueprint(client_manager, url_prefix='/client_manager')
# app.register_blueprint(job_manager, url_prefix='/job_manager')


def run_server():
    '''
    Method to create a thread for the server process
    '''
    app.run(port=args['controller_port'], debug=False,
            threaded=True, host='0.0.0.0')


server = Process(target=run_server, name="controller_server_process")


def start_server():
    '''
    Method to start the server
    '''
    if check_local_port_bind(args['controller_port']):
        server.start()
        print(
            f'Controller server listening on port {args["controller_port"]}.')
    else:
        print(
            f'Cannot start controller server! Port {args["controller_port"]} already in use.')
        args['controller_avl'] = False

    peer_manager.set_controller_port(
        args['controller_avl'], args['controller_port'])


def stop_server():
    '''
    Method to stop the server, it joins it, and then exit will be called
    '''
    print('Stopping server...')
    if server.is_alive():
        server.terminate()
        server.join()
