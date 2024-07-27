from time import sleep
import procmon.system_level as system_level
import procmon.process_level as process_level


def runner(pid: int):
    while True:
        print("System")
        print(system_level.get_load_averages())
        print(system_level.get_ram_info())
        print(system_level.get_unique_id())
        print("\nProcess")
        print(process_level.get_cpu_usage(pid))
        print(process_level.get_memory_usage(pid))

        sleep(1)
