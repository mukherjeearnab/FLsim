'''
Peer Discovery and Ping Process
'''
import traceback
from time import sleep
from multiprocessing import Process
from env import env
from helpers.argsparse import args
from helpers.http import get, post
from helpers.logging import logger
from apps.gossip.peer_management import PeerManager

peer_manager = PeerManager()


def init_discovery_process():
    '''
    Initiates the discovery process.
    (1) Register on Bootnode and Get all nodes from the boot node
    (2) Ping all nodes from the boot node and register with them
    (3) If registered, Add the new nodes to the discovered peer list
    (4-A) Iteratively do:
        1. Get node records from all (connected) peers
        2. Try registering with all (new) peers
        3. If registered, Add them to the discovered peer list
    (4-B) Iteratively do:
        1. For all peers in the discovered peer list alive ping them every DISCOVERY_INTERVAL
    '''

    # (1) Get all nodes from the BOOT node
    nodes = dict()
    try:
        if not args['is_bootnode']:
            logger.info(
                f"Trying to establish connection with bootnode @ [{args['bootnode_url']}].")
            bootnode_info = get(
                f"{args['bootnode_url']}/peer/node_info", timeout=60)
            bootnode_ip = args['bootnode_url'].split(':')[1].replace('//', '')

            # 1-A Register with bootnode
            register_discovered_nodes(
                bootnode_info['node_id'], bootnode_info, ip_override=bootnode_ip)

            # 1-B Get all nodes of bootnode
            nodes = get(
                f"{args['bootnode_url']}/peer/get_alive_peers", timeout=60)
    except Exception:
        logger.error(
            f"Error connecting to bootnode @ {args['bootnode_url']}\n{traceback.format_exc()}")

    # (2) Ping all nodes from the boot node and register with them
    # (3) add the pinged nodes to peer discovery registry
    for node_id, node_info in nodes.items():
        if node_id != peer_manager.node_info()['node_id']:
            register_discovered_nodes(node_id, node_info)

    # (4) Start the background process
    discovery_process = Process(
        target=background_process, name="discovery_process", daemon=True)
    discovery_process.start()


def background_process():
    '''
    Background Process to run 4-A and 4-B processes
    '''

    while True:
        try:
            # first ping all connected nodes
            alive_ping_process()

            # then discover for new nodes
            find_new_nodes_and_connect()

            sleep(env['DISCOVERY_INTERVAL'])
        except KeyboardInterrupt:
            print('Exiting Discovery Process')
            exit()


def find_new_nodes_and_connect():
    '''
    Find new nodes from the peer discovery protocol and 
    add them to the peer discovery registry
    '''

    connected_peers = peer_manager.get_alive_peers()

    logger.info(
        f'[Peer Discovery] Connected to {len(connected_peers.keys())} peers.')

    # 1. Get node records from all (connected) peers
    for node_id, node_info in connected_peers.items():
        # logger.info(f"Fetching peer list from node [{node_id}]")
        try:
            nodes = get(
                f"http://{node_info['idis_ip']}:{node_info['gossip_port']}/peer/get_alive_peers", timeout=60)
        except:
            logger.warning(f"Error fetching peer list from node [{node_id}]")
            continue

        for _node_id, _node_info in nodes.items():
            # 2. Try registering with all (new) peers
            # 3. If registered, Add them to the discovered peer list
            if _node_id not in connected_peers and _node_id != peer_manager.node_info()['node_id']:
                register_discovered_nodes(_node_id, _node_info)


def alive_ping_process():
    '''
    Alive ping process, which pings all connected and alive peers 
    using the gossip alive ping
    '''
    # 1. For all peers in the discovered peer list alive ping them every DISCOVERY_INTERVAL
    connected_peers = peer_manager.get_alive_peers()

    # 1. Get node records from all (connected) peers
    for node_id, node_info in connected_peers.items():
        try:
            post(
                f"http://{node_info['idis_ip']}:{node_info['gossip_port']}/peer/alive_ping",
                {'node_id': peer_manager.node_info()['node_id']}, timeout=30)
        except:
            logger.warning(
                f"Error pinging node [{node_id}] @ {node_info['idis_ip']}:{node_info['gossip_port']}")


def register_discovered_nodes(node_id: str, node_info: dict, ip_override=None):
    '''
    Try Registering with nodes found
    '''
    my_id, my_info = peer_manager.node_info(
    )['node_id'], peer_manager.node_info()
    node_idis_ip = None
    old_idis = node_info['idis_ip'] if ip_override is None else ip_override
    logger.info(
        f"Trying to establish connection with node [{node_id}] with IDIS IP [{old_idis}].")
    try:
        post(f"http://{old_idis}:{node_info['gossip_port']}/peer/register_node",
             {'node_id': my_id, 'node_info': my_info}, timeout=30)
        # logger.success(
        #     f"Successfully established connection with node [{node_id}].")
        node_idis_ip = old_idis
    except Exception:
        logger.warning(
            f"Failed to establish connection with node [{node_id}] with IDIS.")
        print(traceback.format_exc())

    if node_idis_ip is None:
        logger.info('Trying to establish connection using host NIC addresses.')
        for ip_address in node_info['ip_addresses']:
            logger.info(
                f"Trying to establish connection with [{node_id}] using [{ip_address}].")
            try:
                post(f"http://{ip_address}:{node_info['gossip_port']}/peer/register_node",
                     {'node_id': my_id, 'node_info': my_info}, timeout=30)
                # logger.success(
                #     f"Successfully established connection with node [{node_id}].")
                node_idis_ip = ip_address
                break
            except:
                pass

    # (3) add node to peer discovery registry
    if node_idis_ip is not None:
        peer_manager.register_node(node_id, node_info, node_idis_ip)
    else:
        logger.warning(
            f"Failed to establish connection with node [{node_id}].")
