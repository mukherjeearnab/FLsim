# Quick Start Guide

## Table of Contents

1. [Installation of pre-requisites](#pre-req)
   1. [Installation of Python dependencies](#python-deps)
   2. [TMUX (optional)](#tmux)
2. [Setting the environment variables](#env)
3. [Deployment](#deploy)
4. [Job deployment](#job-deploy)
5. [Performance logging](#performance-log)

## Installation of Pre-requisites <a name="pre-req"></a>

To get started, first install a Python environment, with `python>=3.8`.

1. Python Dependencies <a name="python-deps"></a>

   ```
   dill==0.3.8
   Flask==3.0.1
   matplotlib==3.8.2
   numpy==1.24.4
   pandas==2.2.0
   python-dotenv==1.0.0
   PyYAML==6.0.1
   Requests==2.31.0
   scikit_learn==1.4.0
   tensorflow==2.15.0.post1
   torch>=1.12.1
   torchvision==0.16.2
   ```

   **NOTE:** Alternatively, the Conda ENV file can also be used to configure the Python requirements, available here: [conda-env.yaml](/conda-env.yaml)

2. Installing Conda and TMUX

   1. Install **Conda**:
      Follow [https://docs.conda.io/projects/miniconda/en/latest/](https://docs.conda.io/projects/miniconda/en/latest/) to install miniconda3.
   2. Install **TMUX**:
      Use `apt` for Ubuntu, `dnf` for RHEL, or use `conda install conda-forge::tmux` if sudo access is not available.

## Setting the Environment Variables <a name="env"></a>

1. Setting the environment variables for `node`:

   1. Open the `node/.env` file and edit the following variables as per the requirements:

      ```bash
      GOSSIP_PORT=5011                      # the gossip port for the bootnode instance
      LOGICON_URL="http://localhost:5555"   # url for the logicon instance
      P2PSTORE_URL="http://localhost:6666"  # url for the kvstore instance
      PERFLOG_URL="http://localhost:7777"   # url for the perflogger instance
      DATADIST_URL="http://localhost:8888"  # url for dataset distributor instance
      DELAY=2.0                             # general delay unit (default 0.5 seconds)
      USE_CUDA=1                            # 1 means to use CUDA, 0 means CPU
      CLIENT_USE_CUDA=1                     # whether client apps should use CUDA
      WORKER_USE_CUDA=0                     # whether worker apps should use CUDA
      DISCOVERY_INTERVAL=20                 # delay for discovery protocol comms
      DETERMINISTIC=1                       # whether to use deterministic learning process
      RANDOM_SEED=0                         # value of random seed for numpy, torch, etc.
      ```

      <!-- **NOTE:** Do edit the bootnode port in the `auto/tmux*.sh` file for node config (line 75). -->

   2. The `perflogger` listening port:
      Open the `perflogger/main.py` file, and edit the listening port (line 105), which by default is `7777`.

   3. The `kvstore` listening port:
      Open the `kvstore/main.py` file, and edit the listening port (line 66), which by default is `6666`.

   4. The `distributor` listening port:
      Open the `distributor/main.py` file, and edit the listening port (line 97), which by default is `8888`.

   5. The `logicon/.env` config:
      Open the `logicon/.env` file, and edit the following config as per requirement.

      ```bash
      LISTEN_PORT=5555  # the logicon server's listening port
      DELAY=0.5         # general delay unit (default 0.5 seconds)
      USE_CUDA=1        # 1 means to use CUDA, 0 means CPU
      ```

   6. According to the changes in the config in the points above, update the `controller/.env` accordingly:

      ```bash
      LOGICON_URL="http://localhost:5555"   # the logicon server's url
      PERFLOG_URL="http://localhost:7777"   # the perflogger server's url
      DATADIST_URL="http://localhost:8888"  # the dataset distributor server's url
      DELAY=0.5                             # general delay unit (default 0.5 seconds)
      ```

## Deployment <a name="deploy"></a>

### Deployment of Core Components

To deploy an instance of FLsim, we need to use the scripts in `/auto`, for auto deployment of core components and nodes.

To get started, we need to first run the `auto/tmux_10n_complete.sh` script using the following arguments:

```bash
bash auto/tmux_10n_complete.sh \
   CUDA_DEVICE_ID \
   CONDA_ENV_NAME \
   STARTING_NODE_ID \
   MAX_NODES \
   ATTACH
```

Here:

- `CUDA_DEVICE_ID` is the device ID, such as `0` for the GPU to be used.
- `CONDA_ENV_NAME` is the name of the conda env to be used, for example `base`.
- `STARTING_NODE_ID` is the starting node ID, such as `0` for nodes starting from `node_0`, or `10` for starting with `node_10`.
- `MAX_NODES` is the maximum number of nodes to be deployed in this tmux session. The number should range from `0` to `10`. `0` means no nodes will be deployed in this tmux session.
- `ATTACH` is used as a `y` or `n`, for whether to attach the tmux window after orchestration or not.

### Deployment of Nodes

To deploy nodes, we can use the `auto/tmux_10c.sh` script for deploying a max of 10 nodes at a time, or we can use the `auto/multi_spawn.sh` script to deploy more than 10 nodes at a time.

**NOTE:** `multi_spawn.sh` uses the `tmux_10c.sh` script under-the-hood.

So, to execute the `auto/tmux_10c.sh` script, we need to execute it as follows:

```bash
bash auto/tmux_10c.sh \
   CUDA_DEVICE_ID \
   CONDA_ENV_NAME \
   BOOTNODE_ADDRESS \
   STARTING_NODE_ID \
   MAX_NODES \
   ATTACH
```

Here:

- `CUDA_DEVICE_ID` is the device ID, such as `0` for the GPU to be used.
- `CONDA_ENV_NAME` is the name of the conda env to be used, for example `base`.
- `BOOTNODE_ADDRESS` is the IP Address / Port of the bootnode, which by default is `5011`.
- `STARTING_NODE_ID` is the starting node ID, such as `0` for nodes starting from `node_0`, or `10` for starting with `node_10`.
- `MAX_NODES` is the maximum number of nodes to be deployed in this tmux session. The number should range from `0` to `10`. `0` means no nodes will be deployed in this tmux session.
- `ATTACH` is used as a `y` or `n`, for whether to attach the tmux window after orchestration or not.

Now, for the bigger picture, executing the `auto/multi_spawn.sh` command looks like this:

```bash
bash auto/multi_spawn.sh \
   CUDA_DEVICE_ID \
   CONDA_ENV_NAME \
   BOOTNODE_NODE \
   STARTING_NODE_ID \
   NUM_SESSIONS
```

Here:

- `CUDA_DEVICE_ID` is the device ID, such as `0` for the GPU to be used.
- `CONDA_ENV_NAME` is the name of the conda env to be used, for example `base`.
- `BOOTNODE_ADDRESS` is the IP Address / Port of the bootnode, which by default is `5011`.
- `STARTING_NODE_ID` is the starting node ID, such as `0` for nodes starting from `node_0`, or `10` for starting with `node_10`.
- `NUM_SESSIONS` is the number of sessions to be launched. Note that each session deploying `10` nodes each. So if we want to launch `100` nodes, we set the `NUM_SESSIONS` to `10`.

**NOTE:** Before we execute the `auto/multi_spawn.sh` script, we need to first deploy the Core Components using the `auto/tmux_10n_complete.sh` script.

## Job deployment

For deploying a job, check out the examples provided at: [Examples](docs/examples/readme.md)
