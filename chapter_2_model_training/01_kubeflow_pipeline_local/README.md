### A simple pipeline in Kubeflow

This is the first example of a pipeline in Kubeflow (KFP). The pipeline just print out a "Hello World".
You'll need two use two bash shells at the same time for this tutorial. Both of them can be in the current folder.


#### 1. Installation of KFP locally

KFP works on Kubernetes-like infrastructures. I tried to create a method for running a pipeline, that could be general enough and be used also on latest Mac M* computers. For this you can look into [kubeflow_locally_mac_m](../kubeflow_locally_mac_m/) where all the needed scripts are grouped.

##### 1a. Install requirements

```bash
bash ../kubeflow_locally_mac_m/1_install_reqs.sh
```

The requirements are `k3d`, `k9s`, `kubefwd`:
- `k3d`: is a wrapper ro tun a minimal Kubernetes distribution in docker. This will make sure our environment looks like Kubernetes
- `k9s`: this is a CLI tool for Kuberentes. We won't use it direclty, but it's needed for installing all the necessary requirements on the system.
- `kubefwd`: this is a tool for Kubernetes Port Forwarding, that works for local development.  We'll need this to do a Port Forwarding, for connecting to the Kubeflow UI locally.

Once the requirements have been installed, we can create our own Kubernetes local clusters. This is done on the last line of the script `1_install_reqs.sh`
```
k3d cluster create localkfp -a 1 -s 1 --servers-memory 8Gb
```
The cluster name will be named `localkfp`. `-a` specifies the number of agents for the cluster, 1 is enough for our purpoposes. `-s` is the number of servers, this is useful for multi-servers tests, but, again, 1 is enough. Finally `--servers-memory` specifies the memory of the server, where 8 GB is enough.

At last, you need `kubectl` to be installed on your laptop too. `kubectl` is the control command for working on Kubernetes. You can find [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/) the guide to install it.

###### 1b. Install KFP pipelines

We'll be installing KFP pipeline version `2.0.3`. The installation is done as if we were on Kuberentes, so we'll use `kubectl` to apply changes on our Kubernetes cluster.
To do this you need to simply run the following script:
```bash
bash ../kubeflow_locally_mac_m/2_install_pipelines.sh
```

###### 1c. Connect to the KFP UI

Now you can finally connect to the Kubeflow UI. In the current bash shell run:
```bash
bash ../kubeflow_locally_mac_m/3_connect_local_host.sh
```

This scripts uses `kubefwd` that will port-forward the kubeflow connection. In this way, you'll see the KFP UI by simply going on your favourite browser and go to `http://ml-pipeline-ui:80`


#### 2 On the second shell, let's install the requirements

Now move on the second shell you've opened. The first shell will guarantee we have the connection to the localhost for Kubeflow UI. In this second shell we will run the Kubeflow pipeline.

First install the needed requirements. You can do this, again, through a `conda` environment or through a `venv`.
For Conda:

```bash
bash scripts/create_conda_env.sh

# activate the conda environment
conda activate kfp_pipeline
```

If you do not want to have `conda` on your laptop, you can install everything in a virtual environment:
```bash
python -m venv venv

# activate your virtual environment
venv/bin/activate
# install the requirements
pip install -r requirements.txt
```

#### 3 Run the pipeline

To run the pipeline in KFP we can just run it with python:
```bash
python pipeline.py
```
The pipeline will be compiled in `yaml`, so it will be readable by KFP. Then, in the `pipeline.py` code:
```python
run = client.create_run_from_pipeline_package(
    'pipeline.yaml',
    arguments={
        'recipient': 'World',
    },
)
```
will create a run from `pipeline.yaml`. The input arguments for the pipeline are given as a dictionary - in this case `recipient: 'World'`.