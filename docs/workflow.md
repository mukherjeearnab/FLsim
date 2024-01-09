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
       for upstream_job in upstream_jobs:
           upstream_job.sendJobDownloadACK(cluster_id / sub_job_id)

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

4. [`clients` + `workers`] **(1)** download the (train/test) datasets from the dataset distributor. **(2)** ACK to their respective cluster's job. **(3)** wait for `ProcessStage` to be set to `1`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the dataset download ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # exec @ logicon
   # from the grass level
   if all_client_DatasetACKed:
       set ClientStage = 2

   if all_workers_DatasetACKed:
       set WorkerStage = 2

   if ClientStage == 2 and WorkerStage == 2:
       for upstream_job in upstream_jobs:
           upstream_job.sendDatasetACK(cluster_id / sub_job_id)

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

   setProcessStage(1)

   def setProcessStage(stage: int):
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

   download_global_parameters()

   update_client_status(3)

   start_local_training()

   # continue here on with submission of trained parameters
   # and set client status to 4
   # and wait for clientStage to be 4
   # wait for processStage to be 1 or 3
   # if 1 restart from download_global_parameters()
   # else if 3, send client status to 5 and exit
   ```
