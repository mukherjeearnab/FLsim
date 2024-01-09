# Workflow

1. [`logicon`] Primary job (for top level cluster) is deployed (mentioning the sub-clusters / clients and workers) as `"job_name"`

   1. [`logicon`] Secondary jobs (for sub-clusters) is deployed (mentioning the sub-clusters / clients and workers) as `"job_name#0"` for single sub-level and `"job_name#0_0"` for double sub-level clusters.

   2. [`logicon`] For the job and all sub-jobs, set `JobsheetDownloadFlag` to `True`.`

   3. [`clients` + `workers`] Download the job sheets from the respective jobs (primary or secondary).

2. [`clients` + `workers`] ACK of the downloaded job sheets and wait for `DatasetDownloadFlag` to be set to `True`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the job sheet ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # from the grass level
   if all_client_ACKed:
       set ClientStage = 1

   if all_workers_ACKed:
       set WorkerStage = 1

   if ClientStage == 1 and WorkerStage == 1:
       for upstream_job in upstream_jobs:
           sendClientJobACKtoUpstreamJob(upstream_job)

   # release modification locks and trigger to set DatasetDownloadFlag
   ```

3. [`(primary+secondary) jobs @ logicon`] sets the Dataset Download Flag true for all the clients and workers in the root cluster to the grass-level clusters in the hierarchy.

   ```python
   # starts from the root level job
   # (activated by the fn. where client and worker stage is set to 1, 1)
   # as shown in the pseudocode in point 2.
   set DownloadDatasetFlag = True

   for downstream_job in downstream_jobs:
       setDownloadDatasetFlag(downstream_job, True)
   ```

4. [`clients` + `workers`] after downloading the (train/test) datasets from the dataset distributor, ACK to their respective cluster's job and wait for `ProcessStage` to be set to `1`. Starts from the grass level as:

   [`(secondary+primary) jobs @ logicon`] does after receiving all the dataset download ACK from their respective clients and workers. (for intermediate level jobs, clients are the sub-clusters under them)

   ```python
   # from the grass level
   if all_client_DatasetACKed:
       set ClientStage = 2

   if all_workers_DatasetACKed:
       set WorkerStage = 2

   if ClientStage == 2 and WorkerStage == 2:
       for upstream_job in upstream_jobs:
           sendClientDatasetACKtoUpstreamJob(upstream_job)

   # release modification locks and trigger to update ProcessStage to 1
   ```

5. [`(primary+secondary) jobs @ logicon`] **(1)** Requests a `client` or `worker` to submit random intitalized `model parameter` to be set as the initial `global parameters`. **(2)** sets the Process Phase / Stage (`ProcessStage`) flag from `0` to `1` true for all the clients and workers in the root cluster to the grass-level clusters in the hierarchy.

   ```python
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
           setProcessStageforDownstreamJob(downstream_job, 1)
   ```
