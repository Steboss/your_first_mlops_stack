#!/bin/bash


export ARTIFACT_REGISTRY_REPO="sawtooth-pipeline"
export PROJECT_ID=$(gcloud config get-value project)
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="sawtooth_template.json"
# create artifact registry
echo "Create Artifact Registry"
gcloud artifacts repositories create ${ARTIFACT_REGISTRY_REPO} \
--repository-format=docker \
--location=europe-west2 \
--description="Artifact Registry for the sawtooth pipeline"

# flex template
echo "*************************"
echo "Build Flex Template"
gcloud dataflow flex-template build gs://${FLEX_BUCKET}/${TEMPLATE_FILE}.json \
--image-gcr-path europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/sawtooth_pipeline:latest \
--sdk-language "PYTHON" \
--metadata-file metadata/metadata.json \
--project ${PROJECT_ID} \
--worker-region europe-west2 \
--env  "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt" \
--env "FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline/processing_logs.py" \
--env "FLEX_TEMPLATE_PYTHON_SETUP_FILE=setup.py" \
--flex-template-base-image "PYTHON3" \
--py-path "."
