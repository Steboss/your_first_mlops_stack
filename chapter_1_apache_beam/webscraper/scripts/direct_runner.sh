#!/bin/bash

export PROJECT_ID=$(gcloud config get-value project)
export RUNNING_REGION="europe-west1"
export PIPELINE_NAME="webscraper-pipeline"
export JOB_NAME="webscraper-pipeline"
export OUTPUT_BUCKET="output-results-for-dataflow-tests"

python pipeline.py --runner DataflowRunner \
        --input gs://flex_templates_my_pipeline/input_words.txt \
        --output-bucket ${OUTPUT_BUCKET} \
        --job_name ${JOB_NAME} \
        --project ${PROJECT_ID} \
        --region ${RUNNING_REGION} \
        --temp_location gs://your-temp-bucket-for-dataflow-tests \
        --staging-location=gs://staging-bucket-for-dataflow-tests