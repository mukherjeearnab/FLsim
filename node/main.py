'''
This is the Commandline interface for managing the server
'''
import logging
from time import sleep
# from state import peer_state
from helpers.argsparse import args
from helpers.networking import get_all_nic_ip
# from helpers.logging import logger
# from helpers import torch as _
from apps.servers import controller, gossip
from apps.gossip.peer_management import PeerManager

# set flask logging level
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# set peer manager object
peer_manager = PeerManager()

peer_manager.set_node_info(args['node_id'], args['is_client'], args['is_worker'],
                           args['is_middleware'], get_all_nic_ip())


# start the servers
if args['controller_avl']:
    controller.start_server()

gossip.start_server()

sleep(1.0)

# set peer manager object


if __name__ == '__main__':
    while True:
        sleep(2)
        print(peer_manager.node_info())
        print(peer_manager.get_peers())
