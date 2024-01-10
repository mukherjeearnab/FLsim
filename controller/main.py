'''
This is the Commandline interface for managing the server
'''
import sys
import logging
from time import sleep
from helpers.logging import logger
# from helpers import torch as _
from commands import job

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


WELCOME_PROMPT = '''Welcome to the DistLearn Controller CLI.
To get started, enter 'help' in the command prompt below.
'''

SINGLE_COMMANDS = ['exit']

# start the server
if __name__ == '__main__':
    print(WELCOME_PROMPT)
    while True:
        print('> ', end='')
        command = input()
        args = command.split(' ')
        if len(args) <= 1 and args[0] not in SINGLE_COMMANDS:
            continue

        # if args[0] == 'server':
        #     server.handle_command(args[1:])

        # elif args[0] == 'client':
        #     client.handle_command(args[1:])

        elif args[0] == 'job':
            job.handle_command(args[1:])

        elif args[0] == 'exit':
            print('Exiting...')
            sys.exit()

        else:
            print('Unknown command: ', command)
