#!/bin/bash

PIPELINE_NAME="sawtooth-window-pipeline"
PROJECT="long-axle-412512"
REGION="us-central1"
NUM_MAX_WORKERS=2
HOME="/home/sbosisio486/dataflow_teaching/3_window_features"

echo "Installing requirements"
sudo pip uninstall --yes -r requirements.txt
sudo pip install -r requirements.txt

echo "MAKE SURE TO EXPORT YOU GOOGLE APPLICTION CREDENTIALS IF IN C.E"

echo "Running pipeline"

python pipeline/processing_logs.py \
    --input-subscription projects/long-axle-412512/subscriptions/sawtooth-window \
    --output-topic projects/long-axle-412512/topics/example-output-sawtooth-window \
    --runner DataflowRunner \
    --region ${REGION} \
    --project ${PROJECT} \
    --temp_location gs://mypipelines-dataflow-temp/ \
    --staging_location gs://dataflow-staging-europe-west2-1028464732444/ \
    --job_name ${PIPELINE_NAME} \
    --requirements_file requirements.txt \
    --max-num-workers ${NUM_MAX_WORKERS} \
    --experiments=enable_data_sampling
