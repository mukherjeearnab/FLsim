# Workflow

1. [`controller`] Loads the job manifest from the `templates` directory, parses it and prepares the dataset and deployment-ready job manifest.

   1. [`controller`] Loads the job manifest from the correcponding Python modules from the `templates` directory.
   2. ['controller] Generates the `dataset_manifest` based on the cluster, client and worker topology and sends it to the dataset `distributor`.
   3. [`distributor`] Uses the `dataset_manifest` to prepare the dataset root and chunks for the clusters, clients and workers.
      1. The `dataset_prep` module is executed to prepare `root dataset`.
      2. Based on the `dataset_manifest`, it prepares the client and worker chunks using the `distribution` module.
      3. Prepares a mapping for clusters of a job for which chunks and ratios for each participant in the job.

2. [`controller`] With the command `job start`, it sends the job manifest to the `logicon`, where the next steps of initialization and execution of the job starts.

   1. First the job is created by sending a `POST` request to `logicon/job/create` route.
   2. Then the job is started by sending another `POST` request to `logicon/job/start` route.

3. [`logicon`] the complete job manifest is loaded as multiple jobs for each cluster.

   1. The jobs for each cluster is deployed with the naming scheme `"job_name#cluster_id"`.

   2. Primary job (for top level cluster) is deployed first (mentioning the sub-clusters / clients and workers) with an alias `"job_name#root"`

   3. [`logicon`] Secondary jobs (for sub-clusters) is deployed (mentioning the sub-clusters / clients and workers) as `"job_name#cluster_id"`.

      a) All job sub-clusters have a `cluster_epochs` parameter, which specified how many cluster rounds will be executed before aggregated global parameters are uploaded to the upstream cluster (similar to a client submitting trained parameters to it's own cluster).

      b) Thus, every job has a local counter `current_epoch` set to `1` initially, and at every `cluster round` it is incremented by `1`.

      c) Finally, when `current_epoch == cluster_epoch`, the `upstream_job.append_client_params` and `upstream_job.update_client_status` are executed by the sub-cluster's job.

      **NOTE:** If `upstream_job` for a job is `null`, i.e., it is a `primary job`, then whatever the `cluster_epoch` set in the job config template, during deployment of the job, `cluster_epoch` will be reset to `1`.

   4. [`logicon`] For the primary job and all sub-jobs, set `download_jobsheet` flag to `True` (in a pre-order sequence).

   5. [`nodes`] Download the job manifests from the `logicon`, and accordingly spawn `client` and `worker` processes for jobs (per cluster) they are enrolled in.

4. [`clients` + `workers`] **(1)** Download the jobsheets. **(2)** ACK of the downloaded job sheets and wait for `client`/`worker` stage to be `1`. **(3)** Initialize the local model. **(4)** wait for `download_dataset` flag to be set to `True`. Starts from the leaf level (with the clients and workers) as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the job sheet ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # exec @ logicon
   # from the leaf level
   if all_client_ACKed:
       set client_stage = 1

   if all_workers_ACKed:
       set worker_stage = 1

   # client/worker side_effect 101
   if client_stage == 1 and worker_stage == 1:
       this.upstream_job.update_client_status(cluster_id, 1)
       emit side_effect(101)

   # release modification locks and trigger to set DatasetDownloadFlag
   ```

5. [`(primary+secondary) jobs @ logicon`] sets the `download_dataset` flag `True` for all the clients and workers in the root cluster to the leaf-level clusters in the hierarchy.

   ```python
   # exec @ logicon
   # starts from the root level job
   # (activated by the fn. where client and worker stage is set to 1, 1)
   # as shown in the pseudocode in point 4.
   def recursive_allow_dataset_download(job):
       job.allow_dataset_download()

       for downstream_job in job.downstream_jobs:
           recursive_allow_dataset_download(downstream_job)
   ```

6. [`clients` + `workers`] **(1)** download the (train/test) datasets from the dataset distributor. **(2)** They send back initial parameters (from local model) to be set as global params, **and then** ACK to their respective cluster's job. **(3)** `clients` wait for `process_stage` to be set to `1`, `workers` wait for `process_stage` to be set to `2`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the dataset download ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # exec @ logicon
   # from the grass level
   if all_client_DatasetACKed:
       set client_stage = 2

   if all_workers_DatasetACKed:
       set worker_stage = 2

   if client_stage == 2 and worker_stage == 2:
       this.upstream_job.update_client_status(cluster_id, 2)
       emit side_effect(102)

   # release modification locks and trigger to update process_stage to 1
   ```

7. [`(primary+secondary) jobs @ logicon`] **(1)** The **Primary** selects a random submitted (_in step **4**_) `model parameter` to be set as the initial `global parameters`. **(2)** sets the Process Phase / Stage (`process_stage`) flag from `0` to `1` true for all the clients and workers in the root cluster to the grass-level clusters in the hierarchy. Also sets the global parameters to every secondary jobs in the sub-clusters.

   ```python
   # exec @ logicon
   # (activated by the fn. where client and worker stage is set to 2, 2)
   # as shown in the pseudocode in point 6.
   # starts with the root job
   def recursive_allow_training(job, global_param):
       job.set_global_model_param(global_param)
       job.allow_start_training()

       for downstream_job in job.downstream_jobs:
           recursive_allow_training(downstream_job)
   ```

8. [`clients`] once the `process_stage` is set to `1`: **(1)** download the `global_model_param`. **(2)** ACK to their respective cluster's job by updating `client_status` to `3` and wait for `client_stage` to be `3`. **(3)** start locally training the model using their local data. Starts from the leaf level as:

   ```python
   # exec @ client
   wait_for_process_stage(1)

   while True:
       download_global_parameters()

       update_client_status(3) # 3: client busy in local training
       wait_for_client_stage(3)

       train_model()

       # submit_trained_parameters()

       # update_client_status(4) # 4: client waiting for global params

       # wait_for_client_stage(4) # wait for all clients to be in 4

       # wait_for_process_stage(2)

       # process_stage = wait_process_stage([1, 3])

       # if process_stage == 3:
       #     update_client_status(5)
       #     break
   ```

   [`(secondary+primary) jobs @ logicon`] will update the `client_stage` in a bottom up approach, if all the `clients` / `sub-clusters` have updated their status to `3`.

   ```python
   # exec @ logicon
   # from the leaf level
   if all_client_status == 3:
       set client_stage = 3
       this.upstream_job.update_client_status(cluster_id, 3)
   ```

9. [`clients`] once done with `local_training()`: **(1)** upload the trained parameters. **(2)** ACK to their respective cluster's job by updating `client_status` to `4`. **(3)** wait for `client_stage` to turn `4` and then wait for `process_stage` to turn `2`. Starts from the leaf level as:

   ```python
   # exec @ client
   # wait_for_process_stage(1)

   while True:
       # download_global_parameters()

       # update_client_status(3) # 3: client busy in local training

       # local_training()

       submit_trained_parameters()

       update_client_status(4) # 4: client waiting for global params

       wait_for_client_stage(4) # wait for all clients to be in 4

       wait_for_process_stage(2)

       # process_stage = wait_process_stage([1, 3])

       # if process_stage == 3:
       #     update_client_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `client` or `sub-cluster` parameters to be submitted. Once all parameters have been submitted, `process_stage` will be updated to `2` _(`clients` / `sub-clusters` will further need to update `client_status` to `4`)_.

   ```python
   # exec @ logicon
   # from the leaf level
   # after all parameters have been submitted by clients and sub-clusters
   if len(submitted_params) == num_clients:
       process_stage = 2

   # also, if all clients / sub-clusters are at status 4 (exec seperately in client_status handler)
   if all_client_status = 4:
       client_status = 4
   ```

   [`workers`] at this point have been waiting for `process_stage` to be `2`. Once `process_stage` is `2`, they: **(1)** download trained client parameters from their respective cluster's job. **(2)** update `worker_status` to `3` (so that eventually `worker_stage` will be `3`). **(3)** start the aggregation process.

   ```python
   # exec @ worker

   while True:
       wait_for_process_stage(2)

       downloaded_params = download_trained_parameters()

       update_worker_status(3)
       wait_for_worker_stage(3)

       aggregated_parameter = run_aggregation_process(downloaded_params)

       # upload_aggregated_parameter(aggregated_parameters)

       # update_worker_status(4)

       # wait_for_worker_stage(4)

       # process_stage = wait_process_stage([1, 3])
       # if process_stage == 3:
       #     update_worker_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `workers` to be in status `3`. Once all `workers` are in `worker_status=3`, `worker_stage` will be updated to `3`.

   ```python
   # exec @ logicon
   if all_worker_status = 3:
       worker_stage = 3
   ```

   [`workers`] at this point have been aggregating the trained parameters. Now they: **(1)** upload the aggregated parameter. **(2)** update `worker_status` to `4` (so that eventually `worker_stage` will be `4`). **(3)** wait for `worker_stage` to turn `4`.

   ```python
   # exec @ worker

   while True:
       # wait_for_process_stage(2)

       # downloaded_params = download_trained_parameters()

       # update_worker_status(3)

       # aggregated_parameter = run_aggregation_process(downloaded_params)

       upload_aggregated_parameter(aggregated_parameters)

       update_worker_status(4)

       wait_for_worker_stage(4)

       # process_stage = wait_process_stage([1, 3])
       # if process_stage == 3:
       #     update_worker_status(5)
       #     break
   ```

   [`(specific cluster) job @ logicon`] waits for all the `workers` to be in status `4`. Once all `workers` are in `worker_status=4`, `worker_stage` will be updated to `4`, and the `Consensus` mechanism will be invoked to select the `updated global parameter`. Once an `updated global parameter` is selected, it is a decision point:

   1. If `upstream_job` is `null`, then the context of `cluster_epoch` is totally ignored and global_model is set and training is resumed.

   2. If `current_epoch` is less than `cluster_epochs`, cluster's global param is set, and training is resumed, and `current_epoch` is incremented by `1`.

   3. If `current_epoch` is equal to `cluster_epochs`, and `upstream_job` is not `null`, then the `updated_global_parameter` is uploaded to the upstream cluster's job. Also, `current_epoch` will be reset to `1`.

   ```python
   # exec @ logicon
   if all_worker_status = 4:
       worker_stage = 4

   if worker_stage == 4:
       # execute consensus and select the updated global parameter
       global_param_update = consensus_select_parameter()

       # decision point: if upstream_clusters is None,
       # this means that this job is the Primary Job, then
       # set global_parameter, and set ProcessPhase to 1
       if job.is_primary:
           recursive_allow_training(job, global_param)
       else:
           if current_epoch == cluster_epochs:
               # upload global parameter to upstream job
               upstream_job.upload_client_parameter(global_param_update)
               upstream_job.update_client_status(4)
               # also reset current_epoch to 1
               current_epoch = 1
           else:
               # resume training and increment epoch by 1
               current_epoch += 1
               recursive_allow_training(job, global_param):

    # definition of setprocess_stage method
    def recursive_allow_training(job, global_param):
       job.set_global_model_param(global_param)
       job.allow_start_training()

       for downstream_job in job.downstream_jobs:
           recursive_allow_training(downstream_job)
   ```

10. [`clients` + `workers`] At this point, the `clients` and the `workers` just have been waiting for the `process_stage` to be `1`. Once the `ProcessPhase` is set to `1`, it starts all over from `Step 6`.

    ```python
    # exec @ client
    wait_for_process_stage(1)

    while True:
        # download_global_parameters()

        # update_client_status(3) # 3: client busy in local training

        # local_training()

        # submit_trained_parameters()

        # update_client_status(4) # 4: client waiting for global params

        # wait_for_client_stage(4) # wait for all clients to be in 4

        process_stage = wait_process_stage([1, 3])
        if process_stage == 3:
            update_client_status(5)
            break
    ```

    ```python
    # exec @ worker

    while True:
        # wait_for_process_stage(2)

        # downloaded_params = download_trained_parameters()

        # update_worker_status(3)

        # aggregated_parameter = run_aggregation_process(downloaded_params)

        # upload_aggregated_parameter(aggregated_parameters)

        # update_worker_status(4)

        # wait_for_worker_stage(4)

        process_stage = wait_process_stage([1, 3])
        if process_stage == 3:
            update_worker_status(5)
            break
    ```
