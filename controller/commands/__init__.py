import re


def sanitize_command(command: str):
    '''
    Sanitize the input command
    '''

    command = command.strip()
    command = re.sub(' +', ' ', command)

    return command
