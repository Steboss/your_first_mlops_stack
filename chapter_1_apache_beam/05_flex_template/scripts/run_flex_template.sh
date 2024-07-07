#!/bin/bash

export PIPELINE_NAME="window-pipeline"
export PROJECT=$(gcloud config get-value project)
export REGION="us-central1" # there may not be availability in europe
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="normal_window_template.json"
export DATAFLOW_GCS_LOCATION="gs://${FLEX_BUCKET}/${TEMPLATE_FILE}"
export NUM_MAX_WORKERS=2
export INPUT_SUBSCRIPTION="projects/${PROJECT}/subscriptions/normal-window-sub"
export OUTPUT_TOPIC="projects/${PROJECT}/topics/example-normal-window"



echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=${REGION} \
--region=${REGION} \
--worker-machine-type=n1-standard-2 \
--max-workers=${NUM_MAX_WORKERS}  \
--num-workers=1  \
--temp-location=gs://temp-bucket-for-dataflow-tests/ \
--staging-location=gs://staging-bucket-for-dataflow-tests/ \
--parameters job_name=${PIPELINE_NAME} \
--parameters project=${PROJECT} \
--parameters region=${REGION} \
--parameters input-subscription=${INPUT_SUBSCRIPTION} \
--parameters output-topic=${OUTPUT_TOPIC}