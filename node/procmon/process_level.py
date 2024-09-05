import os
import psutil


def get_cpu_usage(pid=os.getpid()):
    '''
    Get the average CPU usage of the process
    '''
    # Get process object
    process = psutil.Process(pid)

    # Get CPU usage as a percentage of each core
    cpu_percent = process.cpu_percent(interval=0.1)
    for child in process.children(recursive=True):
        cpu_percent += child.cpu_percent(interval=0.1)

    # Get the number of CPU cores
    num_cores = psutil.cpu_count()

    # Calculate actual CPU usage
    actual_cpu_usage = cpu_percent / num_cores

    return cpu_percent, num_cores, actual_cpu_usage


def get_memory_usage(pid=os.getpid()):
    '''
    Get the memory usage of the process
    '''
    # Get process object
    process = psutil.Process(pid)

    # Get memory info
    memory_info = process.memory_info()

    # Extract RSS and VMS
    rss = memory_info.rss
    vms = memory_info.vms

    return (rss, vms)
