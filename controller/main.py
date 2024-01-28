'''
This is the Commandline interface for managing the server
'''
import os
import sys
import logging
import readline

from commands import job, sanitize_command

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

readline.set_history_length(1000)
comm_history = './.comm_history'
if os.path.exists(comm_history):
    readline.read_history_file(comm_history)

WELCOME_PROMPT = '''Welcome to the DistLearn Controller CLI.
To get started, enter 'help' in the command prompt below.
'''

SINGLE_COMMANDS = ['exit']


# start the server
if __name__ == '__main__':
    print(WELCOME_PROMPT)
    while True:
        try:
            command = input('> ')

            # sanitize the input
            command = sanitize_command(command)

            args = command.split(' ')
            if len(args) <= 1 and args[0] not in SINGLE_COMMANDS:
                continue

            elif args[0] == 'job':
                job.handle_command(args[1:])

            elif args[0] == 'exit':
                readline.write_history_file(comm_history)
                print('Exiting...')
                sys.exit()
            else:
                print('Unknown command: ', command)

        except KeyboardInterrupt:
            readline.write_history_file(comm_history)
            print('Exiting...')
            sys.exit()
