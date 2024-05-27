#!/bin/bash

export PIPELINE_NAME="window-pipeline"
export PROJECT=$(gcloud config get-value project)
export REGION="europe-west2"
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="normal_window_template.json"
export DATAFLOW_GCS_LOCATION="gs://${FLEX_BUCKET}/${TEMPLATE_FILE}.json"
export NUM_MAX_WORKERS=2
export INPUT_SUBSCRIPTION="projects/${PROJECT_ID}/subscriptions/normal-window"
export OUTPUT_TOPIC="projects/${PROJECT_ID}/topics/example-normal-window"



echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=${REGION} \
--region=${REGION} \
--worker-machine-type=n1-standard-2 \
--max-workers=${NUM_MAX_WORKERS}  \
--num-workers=1  \
--temp_location gs://mypipelines-dataflow-temp/ \
--staging_location gs://dataflow-staging-europe-west2-1028464732444/ \
--parameters job_name=${PIPELINE_NAME} \
--parameters project=${PROJECT} \
--parameters region=${REGION} \
--parameters input-subscription=${INPUT_SUBSCRIPTION} \
--parameters output-topic=${OUTPUT_TOPIC}