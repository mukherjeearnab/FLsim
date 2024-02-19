import psutil
from time import sleep, time
import os
import getpass
import numpy
from dotenv import load_dotenv
from helpers.http import get

# import environment variables
load_dotenv()

WRITE_BUFFER_SIZE = 50
LOG_INTERVAL = 0.1
P2PSTORE_URL = os.getenv('P2PSTORE_URL')


def monitor_process(outfile: str, event):
    '''
    Peridically monitor the system stats and write then to csv file
    '''

    # write the csv headers
    with open(outfile, 'w') as f:
        f.write('timestamp,cpu_usage,memory_usage,network_usage\n')

    csv_line_buffer = []

    while True:
        cpu_percent = get_cpu_usage()
        memory_used = psutil.virtual_memory().used

        # get network usage from kvstore api
        network_usage = get_network_usage()

        # get timestamp
        timestamp = time()

        line = f'{timestamp},{cpu_percent},{memory_used},{network_usage}\n'

        csv_line_buffer.append(line)

        if len(csv_line_buffer) >= WRITE_BUFFER_SIZE or event.is_set():
            with open(outfile, 'a', encoding='utf8') as f:
                f.writelines(csv_line_buffer)

            csv_line_buffer = []

            if event.is_set():
                break

        sleep(LOG_INTERVAL)

    print("Exiting Res Logger Thread")


def get_network_usage():
    '''
    Make an HTTP Request to get network usage from kvstore
    '''

    url = f'{P2PSTORE_URL}/size'

    try:
        size = get(url, {})['size']
    except:
        size = -1

    return size


def get_cpu_usage():
    '''
    Get the CPU usage of current user
    '''
    username = getpass.getuser()
    cpu_pers = []

    for p in psutil.process_iter():
        try:
            if p.username() == username:
                percent = p.cpu_percent()
                if percent > 0.05:
                    cpu_pers.append(percent)
        except:
            pass

    return numpy.mean(cpu_pers)
