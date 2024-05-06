#!/bin/bash

PIPELINE_NAME="window-pipeline"
PROJECT="long-axle-412512"
REGION="europe-west1"
DATAFLOW_GCS_LOCATION="gs://flex_templates_my_pipeline/window_template.json"
NUM_MAX_WORKERS=2

echo "Running Flex Template"
gcloud dataflow flex-template run ${PIPELINE_NAME} \
--project=${PROJECT} \
--template-file-gcs-location=${DATAFLOW_GCS_LOCATION} \
--worker-region=${REGION} \
--region=${REGION} \
--worker-machine-type=n1-standard-2 \
--max-workers=$NUM_MAX_WORKERS  \
--num-workers=1  \
--temp-location=gs://mypipelines-dataflow-temp/ \
--staging-location=gs://dataflow-staging-europe-west2-1028464732444/ \
--parameters job_name=window-pipeline \
--parameters project=${PROJECT} \
--parameters region=${REGION} \
--parameters input-subscription=projects/long-axle-412512/subscriptions/example-window-pipeline-sub \
--parameters output-topic=projects/long-axle-412512/topics/example-output-window-pipeline