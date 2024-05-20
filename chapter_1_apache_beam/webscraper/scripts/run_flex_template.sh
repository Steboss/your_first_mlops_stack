#!/bin/bash

export ARTIFACT_REGISTRY_REPO="webscraper-pipeline"
export PROJECT_ID=$(gcloud config get-value project)
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="webscraper_template.json"
export RUNNING_REGION="europe-west1"
export DATAFLOW_GCS_LOCATION="gs://${FLEX_BUCKET}/${TEMPLATE_FILE}.json"
export PIPELINE_NAME="webscraper-pipeline"
export JOB_NAME="webscraper-pipeline"
export OUTPUT_BUCKET="output-results-for-dataflow-tests"
NUM_MAX_WORKERS=2

if ! gsutil ls -p ${PROJECT_ID} gs://${OUTPUT_BUCKET} &> /dev/null;
    then
        echo creating gs://${OUTPUT_BUCKET} ... ;
        gcloud storage buckets gs://${OUTPUT_BUCKET} --location eu-west-2;
        sleep 5;
    else
        echo "Bucket ${OUTPUT_BUCKET} already exists!"
fi

echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT_ID} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=${RUNNING_REGION} \
--region=${RUNNING_REGION} \
--worker-machine-type=n1-standard-2 \
--max-workers=$NUM_MAX_WORKERS  \
--num-workers=1  \
--temp-location=gs://temp-bucket-for-dataflow-tests/ \
--staging-location=gs://staging-bucket-for-dataflow-tests/ \
--parameters job_name=${JOB_NAME} \
--parameters project=${PROJECT_ID} \
--parameters region=${REGION} \
--parameters input-list=apple \
--parameters output-bucket=${OUTPUT_BUCKET}