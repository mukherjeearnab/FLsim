'''
Commands for Server
'''

from typing import List
from apps.job.load import load_job
from apps.job.start import start_job
from apps.job.abort import abort_job
from apps.job.delete import delete_job


def handle_command(args: List[str]) -> None:
    '''
    Handle the Forwarded Commands
    '''
    if len(args) == 4 and (args[0] == 'load' and args[2] == 'as'):
        load_job(job_config=args[1], job_name=args[3])

    elif args[0] == 'start':
        start_job(job_name=args[1])

    elif args[0] == 'delete':
        delete_job(job_name=args[1])

    elif args[0] == 'abort':
        abort_job(job_name=args[1])

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
abort\tAbort the job, and sub-jobs.
delete\tDelete a running job.
''')
