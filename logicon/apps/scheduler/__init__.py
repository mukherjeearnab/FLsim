

def schedule_job_status(participants: dict, job_status: dict, exec_params: dict, node_id: str, node_type: str, max_parallel=2):
    '''
    [add documentation here]
    '''
    process_stage = job_status['process_stage']
    global_round = job_status['global_round']
    clients = participants['clients']
    workers = participants['workers']

    num_client_params = len(exec_params['client_trained_params'])
    num_worker_params = len(exec_params['worker_aggregated_params'])

    job_status['start_scheduled_execution'] = False

    max_parallel = global_round - 1
    max_parallel = max(max_parallel, 1)

    # if process stage is client training
    if process_stage == 1 and node_type == 'client':
        clients_to_allow = []
        for i in range(max_parallel):
            node_index = min(i+num_client_params, len(clients)-1)
            clients_to_allow.append(clients[node_index])
            # print("CLIENTS TO ALLOW", clients_to_allow)

        if node_id in clients_to_allow:
            job_status['start_scheduled_execution'] = True

        return job_status

    elif process_stage == 2 and node_type == 'worker':
        workers_to_allow = []
        for i in range(min(max_parallel, len(workers))):
            node_index = min(i+num_worker_params, len(workers)-1)
            workers_to_allow.append(workers[node_index])

        if node_id in workers_to_allow:
            job_status['start_scheduled_execution'] = True

        return job_status

    # if process_stage is none out of 1 or 3
    return job_status
