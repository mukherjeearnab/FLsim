# Quick Start Guide

## Table of Contents

1. [Installation of pre-requisites](#pre-req)
   1. [Installation of Python dependencies](#python-deps)
   2. [TMUX (optional)](#tmux)
2. [Setting the environment variables](#env)
3. [Deployment](#deploy)
   1. [Core components](#core-deploy)
   2. [Node deployment](#node-deploy)
4. [Job deployment](#job-deploy)
   1. [Loading a job](#job-load)
   2. [Creating and starting a job](#start-job)
5. [Performance logging](#performance-log)

## Installation of Pre-requisites <a name="pre-req"></a>

To get started, first install a Python environment, with `python>=3.8`.

1. Python Dependencies <a name="python-deps"></a>

   ```
   Flask==3.0.1
   matplotlib==3.8.2
   numpy==1.24.4
   pandas==2.2.0
   python-dotenv==1.0.0
   PyYAML==6.0.1
   Requests==2.31.0
   scikit_learn==1.4.0
   torch>=1.12.1
   torchvision==0.16.2
   ```

2. Installing Conda and TMUX

   1. Install **Conda**:
      Follow [https://docs.conda.io/projects/miniconda/en/latest/](https://docs.conda.io/projects/miniconda/en/latest/) to install miniconda3.
   2. Install **TMUX**:
      Use `apt` for Ubuntu, `dnf` for RHEL, or use `conda install conda-forge::tmux` if sudo access is not available.

## Setting the Environment Variables <a name="env"></a>

1. Setting the environment variables for `node`:

   1. Open the `node/.env` file and edit the following variables as per the requirements:

      ```bash
      GOSSIP_PORT=5000                      # the gossip port for the bootnode instance
      LOGICON_URL="http://localhost:5555"   # url for the logicon instance
      P2PSTORE_URL="http://localhost:6666"  # url for the kvstore instance
      PERFLOG_URL="http://localhost:7777"   # url for the perflogger instance
      DATADIST_URL="http://localhost:8888"  # url for dataset distributor instance
      DELAY=0.5                             # general delay unit (default 0.5 seconds)
      USE_CUDA=1                            # 1 means to use CUDA, 0 means CPU
      DISCOVERY_INTERVAL=20                 # delay for discovery protocol comms
      ```

      **NOTE:** Do edit the bootnode port in the `auto/tmux*.sh` file for node config (line 75).

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
