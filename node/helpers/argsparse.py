'''
Args Parser Module
'''
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--node_id", required=True)
parser.add_argument("-b", "--bootnode")
parser.add_argument("-cn", "--controller")
parser.add_argument("-g", "--gossip")

# node role args
parser.add_argument("-c", "--client", action="store_true")
parser.add_argument("-m", "--middleware", action="store_true")
parser.add_argument("-w", "--worker", action="store_true")

# extra args
parser.add_argument("-d", "--debug", action="store_true")


parsed_args = parser.parse_args()

args = dict()

# process node_id
args['node_id'] = str(parsed_args.node_id)

# process bootnode args
if parsed_args.bootnode:
    args['is_bootnode'] = False
    if parsed_args.bootnode.isdigit():
        args['bootnode_url'] = f'http://localhost:{parsed_args.bootnode}'
    elif 'http' in parsed_args.bootnode:
        args['bootnode_url'] = parsed_args.bootnode
    else:
        args['bootnode_url'] = f'http://{parsed_args.bootnode}'
else:
    args['is_bootnode'] = True

# process controller args
if parsed_args.controller:
    args['controller_avl'] = int(parsed_args.controller) != 0
    args['controller_port'] = int(parsed_args.controller)
else:
    args['controller_avl'] = False
    args['controller_port'] = int(os.getenv('CONTROL_PORT'))

# process gossip args
if parsed_args.gossip:
    if str(parsed_args.gossip) == 'r':
        args['random_gossip_port'] = True
    else:
        args['random_gossip_port'] = False
        args['gossip_port'] = int(parsed_args.gossip)
else:
    args['gossip_port'] = int(os.getenv('GOSSIP_PORT'))
    args['random_gossip_port'] = False

# process role args
args['is_client'] = parsed_args.client
args['is_middleware'] = parsed_args.middleware
args['is_worker'] = parsed_args.worker

args['debug'] = parsed_args.debug
