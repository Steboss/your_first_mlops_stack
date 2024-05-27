#!/bin/bash

export PROJECT_ID=$(gcloud config get-value project)

python pipeline.py --runner DataflowRunner \
        --input gs://dataflow-samples/shakespeare/kinglear.txt \
        --output-file gs://output-results-for-dataflow-tests/output-word-count-${DATE}.txt \
        --job_name wordcount-pipeline \
        --project ${PROJECT_ID} \
        --region europe-west1 \
        --temp_location gs://your-temp-bucket-for-dataflow-tests