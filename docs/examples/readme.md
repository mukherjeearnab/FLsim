# Examples

To get started with FLsim, trying out some example experiments are a perfect choice to get used to how the framework works. Here are some examples:

## CIFAR-10 Example

In this example we will execute an experiment on CIFAR-10 using 2 clients, using the PyTorch library.

Following are the files required to run the experiment:

1. The Job Configuration [cifar10_torch_2c.yaml](/templates/job/cifar10_torch_2c.yaml)
2. The FL Strategy File [cifar10_cnn_fedavg.py](/templates/strategy/cifar10_cnn_fedavg.py)
3. The Dataset File [cifar10_torch.py](/templates/dataset/cifar10_torch.py)

### Loading the job

Now, on the terminal of the `Controller`, which is launched using the `auto/tmux_10n_complete.sh` script, we need to first load the job as:

```bash
job load job_config_file as job_alias
```

Here the `job_config_file` is the name of the `.yaml` config file we will be using, without the `.yaml` extension. The `job_alias` is an alias name for the job to uniquely recognise the experiment we are running.

The exact command for this experiment will be:

```bash
job load cifar10_torch_2c as cifar10_exp1
```

**NOTE:** We can also skip the `job_alias` part, which will cause the system to use the job config name as the project/experiment name. The command will look like: `job load job_config_file`

Once the command is executed, the dataset preperation and check will be performed to load the job.

### Starting the job

Next, we need to start the job using:

```bash
job start job_name
```

Here, `job_name` will be the `job_alias`, if an alias is mentioned, or the `job_config_file` otherwise. The exact command for this experiment will be:

```bash
job start cifar10_exp1
```

Once the command is executed, the job will start, and FL training will be performed. To evaluate the FL training performance, we can check the Performance Log available in the `perflogger/projects` directory. In this directory, a folder with the `job_name` along with the date and time of the job will be available. In this directory, a a file named `perflog.csv` will contain the detailed training performance of all the nodes every FL round.
