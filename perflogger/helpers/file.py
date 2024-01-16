'''
File Handling Module
'''
from os.path import exists
from os import makedirs


def write_file(file_name: str, file_path: str, content: str, mode='w') -> None:
    '''
    Write string contents to file
    '''
    create_dir_struct(file_path)
    with open(f'{file_path}/{file_name}', mode, encoding='utf8') as f:
        f.write(content)


def create_dir_struct(path: str) -> None:
    '''
    Creates a directory structure, if it does not exist
    '''

    if not exists(path):
        makedirs(path)
