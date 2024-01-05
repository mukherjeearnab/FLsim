'''
Application Logic for Peer Management
'''
from time import time
from state import peer_state
from helpers.semaphore import Semaphore

# Client alove threshold in seconds
ALIVE_THRESHOLD = 10

UPDATE_LOCK = Semaphore()


class PeerManager(object):
    '''
    Client Count manager class
    '''

    def __init__(self):
        '''
        constructor
        '''

    def node_info(self) -> list:
        '''
        Get node's self information
        '''
        peer_info = peer_state['node_info']
        return peer_info

    def set_node_info(self, node_id: str, is_client: bool, is_worker: bool, is_middleware: bool, ip_addresses: str) -> None:
        '''
        Set node's self information
        '''
        UPDATE_LOCK.acquire()

        # fetch updated managed dict
        peer_info = peer_state['node_info']

        peer_info['node_id'] = node_id
        peer_info['is_client'] = is_client
        peer_info['is_worker'] = is_worker
        peer_info['is_middleware'] = is_middleware
        peer_info['ip_addresses'] = ip_addresses

        # update managed dict
        peer_state['node_info'] = peer_info

        UPDATE_LOCK.release()

    def set_gossip_port(self, port: int) -> None:
        '''
        Set node's gossip port
        '''
        UPDATE_LOCK.acquire()

        # fetch updated managed dict
        peer_info = peer_state['node_info']

        peer_info['gossip_port'] = port

        # update managed dict
        peer_state['node_info'] = peer_info

        UPDATE_LOCK.release()

    def set_controller_port(self, available: bool, port: int) -> None:
        '''
        Set node's controller port
        '''
        UPDATE_LOCK.acquire()

        # fetch updated managed dict
        peer_info = peer_state['node_info']

        peer_info['controller'] = {
            'port': port,
            'available': available
        }

        # update managed dict
        peer_state['node_info'] = peer_info

        UPDATE_LOCK.release()

    def get_peers(self) -> list:
        '''
        Get discovered peers of the node
        '''
        # fetch updated managed dict
        peers = peer_state['peers']
        return peers

    def get_alive_peers(self) -> list:
        '''
        Get discovered and alive peers of the node
        '''
        # fetch updated managed dict
        peers = peer_state['peers']

        alive_peers = dict()
        for peer in peers.keys():
            if (int(time()) - peers[peer]['last_ping']) <= ALIVE_THRESHOLD:
                alive_peers[peer] = peers[peer]

        return alive_peers

    def register_node(self, node_id: str, node_info: dict, idis_ip: str) -> dict:
        '''
        Register a node on the cuttent node's comm dir
        '''
        # ip address of node which is used to discovery
        node_info['idis_ip'] = idis_ip
        # alive ping
        node_info['last_ping'] = int(time())

        UPDATE_LOCK.acquire()

        # fetch updated managed dict
        peers = peer_state['peers']

        peers[node_id] = node_info

        # update managed dict
        peer_state['peers'] = peers
        UPDATE_LOCK.release()

        return peers[node_id]

    def alive_ping(self, node_id: str) -> bool:
        '''
        update alive ping of a node
        '''
        UPDATE_LOCK.acquire()

        # fetch updated managed dict
        peers = peer_state['peers']

        if node_id in peers:
            peers[node_id]['last_ping'] = int(time())

            # update managed dict
            peer_state['peers'] = peers

            UPDATE_LOCK.release()

            return True
        else:
            UPDATE_LOCK.release()
            return False
