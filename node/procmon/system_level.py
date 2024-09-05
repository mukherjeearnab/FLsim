import uuid
import os
import psutil


def get_load_averages():
    '''
    Get the load average as a tuple of 1, 5, 15 minute
    '''

    # Get load averages
    return psutil.getloadavg()


def get_num_cpus():
    '''
    Get the number of CPU cores / threads

    Returns the count of Physical Cores and Logical (thread) CPUs
    '''

    # Get the number of logical CPU cores (including hyper-threading)
    logical_cores = psutil.cpu_count(logical=True)

    # Get the number of physical CPU cores (excluding hyper-threading)
    physical_cores = psutil.cpu_count(logical=False)

    return physical_cores, logical_cores


def get_ram_info():
    '''
    Get the memory information as 
    total memory, free memory, and used memory
    '''
    # Get physical memory (RAM) info
    mem = psutil.virtual_memory()

    # Extract total, available, and used memory
    total_memory = mem.total
    free_memory = mem.available
    used_memory = mem.used

    return total_memory, free_memory, used_memory


def get_unique_id():
    '''
    generates a UUID for the machine and returns it
    '''
    # Generate a UUID based on the MAC address
    unique_id = uuid.getnode()  # Gets the MAC address and creates a UUID
    return unique_id
