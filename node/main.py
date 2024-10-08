'''
This is the Commandline interface for managing the server
'''
import os
import sys
import signal
import logging
from time import sleep
from threading import Thread
# from state import peer_state
from helpers.argsparse import args
from helpers.networking import get_all_nic_ip
# from helpers.logging import logger
# from helpers import torch as _
from state import jobs_proc_state
from apps.servers import controller, gossip
from apps.gossip.peer_management import PeerManager
from apps.gossip.discovery import init_discovery_process
from apps.job import job_keep_alive_process
from procmon import runner

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
init_discovery_process()

pid = os.getgid()
print("PID: ", pid)
sleep(1.0)

# # procmon
# procmon = Thread(target=runner, args=(
#     pid,))


def sigint_handler(signum, frame):

    # stop the servers and exit
    controller.stop_server()
    gossip.stop_server()

    # stop all job processes
    for _, proc in jobs_proc_state.items():
        proc.kill()
        proc.join()

    procmon.join()
    sys.exit()


signal.signal(signal.SIGINT, sigint_handler)


if __name__ == '__main__':
    print("PROCPID", os.getpid())
    # procmon = Thread(target=runner, args=(
    #     os.getpid(),)).start()
    job_keep_alive_process()
