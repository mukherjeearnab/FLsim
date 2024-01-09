# Workflow

1. [`logicon`] Primary job (for top level cluster) is deployed (mentioning the sub-clusters / clients and workers) as `"job_name"`

   1. [`logicon`] Secondary jobs (for sub-clusters) is deployed (mentioning the sub-clusters / clients and workers) as `"job_name#0"` for single sub-level and `"job_name#0_0"` for double sub-level clusters.

   2. [`logicon`] For the job and all sub-jobs, set `JobsheetDownloadFlag` to `True`.`

   3. [`clients` + `workers`] Download the job sheets from the respective jobs (primary or secondary).

2. [`clients` + `workers`] **(1)** Download the jobsheets. **(2)** ACK of the downloaded job sheets. **(3)** wait for `DatasetDownloadFlag` to be set to `True`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the job sheet ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # exec @ logicon
   # from the grass level
   if all_client_ACKed:
       set ClientStage = 1

   if all_workers_ACKed:
       set WorkerStage = 1

   if ClientStage == 1 and WorkerStage == 1:
       this.upstream_job.sendJobDownloadACK(cluster_id / sub_job_id)

   # release modification locks and trigger to set DatasetDownloadFlag
   ```

3. [`(primary+secondary) jobs @ logicon`] sets the Dataset Download Flag true for all the clients and workers in the root cluster to the grass-level clusters in the hierarchy.

   ```python
   # exec @ logicon
   # starts from the root level job
   # (activated by the fn. where client and worker stage is set to 1, 1)
   # as shown in the pseudocode in point 2.
   set DownloadDatasetFlag = True

   for downstream_job in downstream_jobs:
       downstream_job.setDatasetDownloadFlag(True)
   ```

4. [`clients` + `workers`] **(1)** download the (train/test) datasets from the dataset distributor. **(2)** ACK to their respective cluster's job. **(3)** `clients` wait for `ProcessStage` to be set to `1`, `workers` wait for `ProcessStage` to be set to `2`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the dataset download ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # exec @ logicon
   # from the grass level
   if all_client_DatasetACKed:
       set ClientStage = 2

   if all_workers_DatasetACKed:
       set WorkerStage = 2

   if ClientStage == 2 and WorkerStage == 2:
       this.upstream_job.sendDatasetACK(cluster_id / sub_job_id)

   # release modification locks and trigger to update ProcessStage to 1
   ```

5. [`(primary+secondary) jobs @ logicon`] **(1)** Requests a `client` or `worker` to submit random intitalized `model parameter` to be set as the initial `global parameters`. **(2)** sets the Process Phase / Stage (`ProcessStage`) flag from `0` to `1` true for all the clients and workers in the root cluster to the grass-level clusters in the hierarchy. Also sets the global parameters to every secondary jobs in the sub-clusters.

   ```python
   # exec @ logicon
   # (activated by the fn. where client and worker stage is set to 2, 2)
   # as shown in the pseudocode in point 4.
   # request for model parameter from a random client / worker. (starts with workers)
   for node in (workers+clients):
       requestInitialParameters(node)

   while True:
       if len(initialParameters) > 0:
           break

   set globalParameter = intialParameters[0]

   setProcessStage(1, globalParameter)

   def setProcessStage(stage: int, globalParameter: dict):
       # starts from the root level job
       set ProcessStage = 1

       for downstream_job in downstream_jobs:
           downstream_job.setGlobalParameter(globalParameter)
           downstream_job.setProcessStage(1)
   ```

6. [`clients`] once the `ProcessStage` is set to `1`: **(1)** download the `globalParameters`. **(2)** ACK to their respective cluster's job by updating `clientStatus` to `3`. **(3)** start locally training the model using their local data. Starts from the grass level as:

   ```python
   # exec @ client
   wait_for_processStage(1)

   while True:
       download_global_parameters()

       update_client_status(3) # 3: client busy in local training

       local_training()

       # submit_trained_parameters()

       # set_client_status(4) # 4: client waiting for global params

       # wait_for_client_stage(4) # wait for all clients to be in 4

       # process_stage = wait_process_stage([1, 3])

       # if process_stage == 3:
       #     set_client_status(5)
       #     break
   ```

   [`(secondary+primary) jobs @ logicon`] will update the `ClientStage` in a hierarchical fashion, if all the `clients` / `sub-clusters` have updated their status to `3`.

   ```python
   # exec @ logicon
   # from the grass level
   if all_client_status == 3:
       set ClientStage = 3
       this.upstream_job.setClientStatus(cluster_id / sub_job_id, 3)
   ```

7. [`clients`] once done with `local_training()`: **(1)** upload the trained parameters. **(2)** ACK to their respective cluster's job by updating `clientStatus` to `4`. **(3)** wait for `ClientStage` to turn `4`. Starts from the grass level as:

   ```python
   # exec @ client
   wait_for_processStage(1)

   while True:
       # download_global_parameters()

       # update_client_status(3) # 3: client busy in local training

       # local_training()

       submit_trained_parameters()

       set_client_status(4) # 4: client waiting for global params

       wait_for_client_stage(4) # wait for all clients to be in 4

       # process_stage = wait_process_stage([1, 3])

       # if process_stage == 3:
       #     set_client_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `client` or `sub-cluster` parameters to be submitted. Once all parameters have been submitted, `ProcessStage` will be updated to `2` _(`clients` / `sub-clusters` will further need to update `ClientStatus` to `4`)_.

   ```python
   # exec @ logicon
   # from the grass level
   # after all parameters have been submitted by clients and sub-clusters
   if len(submitted_params) == num_clients:
       ProcessStage = 2

   # also, if all clients / sub-clusters are at status 4 (exec seperately in ClientStatus handler)
   if all_client_status = 4:
       ClientStage = 4
   ```

   [`workers`] at this point have been waiting for `ProcessStage` to be `2`. Once `ProcessStage` is `2`, they: **(1)** download trained parameters from their respective cluster's job. **(2)** update `WorkerStatus` to `3` (so that eventually `WorkerStage` will be `3`). **(3)** start the aggregation process.

   ```python
   # exec @ worker

   while True:
       wait_for_processStage(2)

       downloaded_params = download_trained_parameters()

       update_worker_status(3)

       aggregated_parameter = run_aggregation_process(downloaded_params)

       # upload_aggregated_parameter(aggregated_parameters)

       # update_worker_status(4)

       # wait_for_workerStage(4)

       # process_stage = wait_process_stage([1, 3])
       # if process_stage == 3:
       #     update_worker_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `workers` to be in status `3`. Once all `workers` are in `WorkerStatus=3`, `WorkerStage` will be updated to `3`.

   ```python
   # exec @ logicon
   if all_worker_status = 3:
       WorkerStage = 3
   ```

   [`workers`] at this point have been aggregating the trained parameters. Now they: **(1)** upload the aggregated parameter. **(2)** update `WorkerStatus` to `4` (so that eventually `WorkerStage` will be `4`). **(3)** wait for `WorkerStage` to turn `4`.

   ```python
   # exec @ worker

   while True:
       # wait_for_processStage(2)

       # downloaded_params = download_trained_parameters()

       # update_worker_status(3)

       # aggregated_parameter = run_aggregation_process(downloaded_params)

       upload_aggregated_parameter(aggregated_parameters)

       update_worker_status(4)

       wait_for_workerStage(4)

       # process_stage = wait_process_stage([1, 3])
       # if process_stage == 3:
       #     update_worker_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `workers` to be in status `4`. Once all `workers` are in `WorkerStatus=4`, `WorkerStage` will be updated to `4`, and the `Consensus` mechanism will be invoked to select the `updated global parameter` and upload to the upstream cluster(s).

   ```python
   # exec @ logicon
   if all_worker_status = 4:
       WorkerStage = 4

   if WorkerStage == 4:
       # execute consensus and select the updated global parameter
       global_param_update = consensus_select_parameter()

       # decision point: if upstream_clusters is not None,
       # this means that this job is the Primary Job, then
       # set global_parameter, and set ProcessPhase to 1
       if upstream_job is not None:
           setProcessStage(1, global_param_update)
       else:
           # upload global parameter to upstream job
           upstream_job.upload_client_parameter(global_param_update)
           upstream_job.update_client_status(4)

    # definition of setProcessStage method
    def setProcessStage(stage: int, globalParameter: dict):
       # starts from the root level job
       set ProcessStage = 1

       for downstream_job in downstream_jobs:
           downstream_job.setGlobalParameter(globalParameter)
           downstream_job.setProcessStage(1)
   ```

8. [`clients` + `workers`] At this point, the `clients` and the `workers` just have been waiting for the `ProcessStage` to be `1`. Once the `ProcessPhase` is set to `1`, it starts all over from `Step 6`.

   ```python
   # exec @ client
   wait_for_processStage(1)

   while True:
       # download_global_parameters()

       # update_client_status(3) # 3: client busy in local training

       # local_training()

       # submit_trained_parameters()

       # set_client_status(4) # 4: client waiting for global params

       # wait_for_client_stage(4) # wait for all clients to be in 4

       process_stage = wait_process_stage([1, 3])
       if process_stage == 3:
           set_client_status(5)
           break
   ```

   ```python
   # exec @ worker

   while True:
       # wait_for_processStage(2)

       # downloaded_params = download_trained_parameters()

       # update_worker_status(3)

       # aggregated_parameter = run_aggregation_process(downloaded_params)

       # upload_aggregated_parameter(aggregated_parameters)

       # update_worker_status(4)

       # wait_for_workerStage(4)

       process_stage = wait_process_stage([1, 3])
       if process_stage == 3:
           update_worker_status(5)
           break
   ```
