#!/bin/bash

export PIPELINE_NAME="sawtooth-pipeline"
export PROJECT_ID=$(gcloud config get-value project)
export RUNNING_REGION="europe-west1"
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="sawtooth_template.json"
export DATAFLOW_GCS_LOCATION="gs://${FLEX_BUCKET}/${TEMPLATE_FILE}.json"
export INPUT_SUBSCRIPTION="projects/${PROJECT_ID}/subscriptions/input-sawtooth-window-sub"
export OUTPUT_TOPIC="projects/${PROJECT_ID}/topics/example-output-sawtooth"


echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT_ID} \
--template-file-gcs-location="${DATAFLOW_GCS_LOCATION}.json" \
--worker-region=${RUNNING_REGION} \
--region=${RUNNING_REGION} \
--worker-machine-type=n1-standard-2 \
--max-workers=2  \
--num-workers=1  \
--temp-location=gs://temp-bucket-for-dataflow-tests/ \
--staging-location=gs://staging-bucket-for-dataflow-tests/ \
--additional-experiments=enable_data_sampling \
--parameters job_name=sawtooth-window-pipeline \
--parameters project=${PROJECT} \
--parameters region=${RUNNING_REGION} \
--parameters input-subscription=${INPUT_SUBSCRIPTION}  \
--parameters output-topic=${OUTPUT_TOPIC}
