'''
Commands for Server
'''

from typing import List
# from apps.job_loader import load_job, start_job
from apps.job.load import load_job
# from helpers.logging import logger

# JOB_PROPS = []


def handle_command(args: List[str]) -> None:
    '''
    Handle the Forwarded Commands
    '''
    if len(args) == 4 and (args[0] == 'load' and args[2] == 'as'):
        load_job(job_config=args[1], job_name=args[3])

    # elif args[0] == 'start':
    #     start_job(job_name=args[1])
    #     # JOB_PROPS.append(job_prop)

    # elif args[0] == 'delete':
    #     delete_job(job_name=args[1])

    # elif args[0] == 'abort':
    #     set_abort(job_name=args[1])

    elif args[0] == 'help':
        _help()

    else:
        print('Unknown server command: ', args)
        _help()


def _help() -> None:
    '''
    Help Method
    '''
    print('''Job Management Help.
Command\tDescription\n
load [job name]\tLoad the config of a job with name [job name].
start [job name]\tStart the job with [job name].
stop\tStop the server.
''')


def stop() -> None:
    '''
    Stop Method to call and stop all running aggregator threads
    '''
    # for i, job in enumerate(JOB_PROPS):
    #     proc = job['aggregator_proc']
    #     if proc.is_alive():
    #         proc.terminate()
    #         proc.join()

    #     logger.info(
    #         f'Terminated Aggregator Process {i+1} out of {len(JOB_PROPS)}')
