### Running example on Dataflow

This code can be run directly on Dataflow. The pipeline we are running is the same as in [01_beam_pipeline](../01_beam_pipeline/). The pipeline will perform a word count on the text on King Lear

#### 1. Setup the Dataflow environment in GCP shell

Follow the slides to setup the GCP environment. Then, activate the GCP Shell in your GCP project:

![Activate Shell](imgs/ActivateShell.png)

#### BEFORE EVERYTHING ELSE

Before everything else, as I am explaining in the lesson, we need to set up our GCP service account. For this I am going to run the following commands, one by one:
```
gcloud init

gcloud config set project $(gcloud config get-value project)

gcloud services enable dataflow compute_component logging storage_component storage_api bigquery pubsub datastore.googleapis.com cloudresourcemanager.googleapis.com

gcloud auth application-default login

gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="user:YOUREMAIL@gmail.com" --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:YOURPROJECTNUMBER-compute@developer.gserviceaccount.com" --role=roles/dataflow.admin
gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:YOURPROJECTNUMBER-compute@developer.gserviceaccount.com" --role=roles/dataflow.worker
gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:YOURPROJECTNUMBER-compute@developer.gserviceaccount.com" --role=roles/stora
```

#### 2. Clone the repo and install requirements

From the bash shell, clone this repository:

```bash
git clone https://github.com/Steboss/your_first_mlops_stack.git
```
Then `cd` in the repository folder and install the requirements:

```bash
cd your_first_mlops_stack/04_wordcount_on_dataflow
pip3 install -r requirements.txt
```

#### 3. Run the pipeline

Finally, direclty form the shell, you can run the pipeline directly on Dataflow:

```bash

PROJECT_ID=$(gcloud config get-value project)


python pipeline.py --runner DataflowRunner \
        --input gs://dataflow-samples/shakespeare/kinglear.txt \
        --output-file gs://output-results-for-dataflow-tests/output-word-count-${DATE}.txt \
        --job_name wordcount-pipeline \
        --project ${PROJECT_ID} \
        --region europe-west1 \
        --temp_location gs://your-temp-bucket-for-dataflow-tests
```