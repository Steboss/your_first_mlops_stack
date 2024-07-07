#!/bin/bash


export ARTIFACT_REGISTRY_REPO="normal-window-pipeline"
export PROJECT_ID=$(gcloud config get-value project)
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="normal_window_template.json"

# echo "Build Docker image"
# docker build --no-cache -t window_pipeline -f docker/Dockerfile .
# echo "Tag Docker image"
# docker tag window_pipeline europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/window_pipeline:latest
# echo "Push Docker image"
# docker push europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/window_pipeline:latest

echo "*************************"
echo "Build Flex Template"
gcloud dataflow flex-template build gs://${FLEX_BUCKET}/${TEMPLATE_FILE} \
--image-gcr-path europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/window_pipeline:latest \
--sdk-language "PYTHON" \
--metadata-file metadata/metadata.json \
--project ${PROJECT_ID} \
--worker-region europe-west2 \
--env  "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt" \
--env "FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline/processing_logs.py" \
--env "FLEX_TEMPLATE_PYTHON_SETUP_FILE=setup.py" \
--flex-template-base-image "PYTHON3" \
--py-path "."