'''
Common Scripts for Client and Worker
'''
from apps.client import setters


def _fail_exit(job_name: str, cluster_id: str, node_type: str):
    '''
    If Getter Method fails, terminate the client/worker process
    and exit
    '''

    # update node status and exit
    setters.update_node_status(job_name, cluster_id, node_type, status=5)
    exit()
