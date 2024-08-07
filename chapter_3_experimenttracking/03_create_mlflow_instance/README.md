### The MLfow infastructure

This code gives you all the needed pieces to build up the MLflow infrastrucuture, so that we can track experiments running in VertexAI

#### 1. Create MLflow Script

The script `create_mlflow_infra.sh` creates a new server on GCP that hosts MLflow.

At first, we're creating the following buckets `gs://mlflowartifactsbucket` that will store all our experiments artifacts.
Then, the script will execute `gcloud compute instances create mlflow-server2 ...` that created the mlflow server. The MLflow server name is `mlflow-server2`. The machin eis of type `e2-medium`and we switch on the option `can-ip-forward`. This option allows to forward the internal and external IP addresses of the machine, so that we can use them to connect to the MLflow server (e.g. we can connect to the MLflow UI as `http://EXTENRAL_IP_OF_THE_MACHINE:5000`).
The machine has its own service account specified as `${PROJECT_NUMBER}-compute@developer.gserviceaccount.com`, and has the authorization to accesso the GCP tools with `--scopes=https://www.googleapis.com/auth/cloud-platform`.
In the creation script you can also notice `tags=mlflow-server...`. This creates a tag on the machine. This tag can be used to attach a specific firewall rule to the machine, so that we will be able to connect to its external ip address and visualize MLflow. If we do not setup this option it would be impossible for us to have a connection between all the gcp tools, e.g. VertexAI, and MLflow. THe final step of the code gives a start up script to the machine that actually install MLflow and set up the ip-forward connection:
```!#/bin/bash
sudo apt-get remove -y --purge man-db
sudo apt-get -y remove python3-blinker
sudo apt-get update
sudo apt-get install -yq git python3 python3-pip
sudo apt-get install -yq blinker
pip3 uninstall -y blinker
pip3 install blinker==1.8.2
echo "pip3 install google-cloud-storage"
pip3 install google-cloud-storage
echo "pip3 install mlflow"
sudo pip3 install mlflow
echo "MLflow version"
mlflow --version
echo "Installing SQLite3..."
sudo apt-get install sqlite3
echo "Sqlite3 installed"
echo "Sqlite version"
sqlite3 --version
echo "Setting up ip"
internalIp=$(hostname -i)
echo "Internal IP = ${internalIp}"
mlflow server --backend-store-uri sqlite:///mlruns.db  --default-artifact-root gs://mlflowartifactsbucket/artifacts --host $internalIp
```
Finally, the script create the following firewall rule:
```
gcloud compute --project=${PROJECT_ID} firewall-rules create mlflow-server \
        --direction=INGRESS \
        --priority=999 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:5000 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=mlflow-server

```
To the `mlflow-server2` machine, that has been tag with `mlflow-server`, we will have that all the services/everybody,`0.0.0.0/0`, will be able to connect to the machine through the port `5000`.


#### 2. Prepare the input data

We are going to create the input data for the tutorial. These data are made through `sklearn` as a fake dataset:
```bash
bash prepare_data/create_bqtable.sh
```

The script will run `prepare_data/generate_data.py`. The generated dataset will be copied on BigQuery so we'll have a dataset and a table to be used.

#### 3. Create the model image AND modify the model code

Again we need to containerized our model:
```bash
bash model/build_image.sh
```
The script will generate the image in `randomforest-vertexai` repository. In this way, we'll use `randomforest-vertexai-mlflow/randomforest_vertexai:latest` in our KFP pipeline.

This is not the same image we created before, as here we have added the MLflow integration.
In particular, you'll have to modify the code between lines 85-95:
```python
logging.info("Setting up MLflow options")
today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
experiment_name = "randomforest-experiments"
client = MlflowClient(tracking_uri="http://EXTERNAL_IP:5000/")
experiment_exists = client.get_experiment_by_name(experiment_name)
if not experiment_exists:
    experiment_id = client.create_experiment(experiment_name)
else:
    experiment_id = experiment_exists.experiment_id
run_name = f"stefano-{today}"
mlflow.set_tracking_uri("http://EXTERNAL_IP:5000/")
```
by replacine `EXTERNAL_IP` with your machine external ip address.


#### 4. Run the KFP pipeline

Before running the pipeline remember to update the lines 293-296:
```python
# query the dataset and export it
sql_query = (
    "SELECT * FROM `YOUR_PROJECT_NAME.learning_vertexai.fake_dataset_1`"
)

```
by replacing `YOUR_PROJECT_NAME` with your project name.

Now that data and image are done, we can run the pipeline:
```bash
bash execute_pipeline.sh
```
