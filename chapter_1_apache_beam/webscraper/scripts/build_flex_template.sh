#!/bin/bash
# copy the file input_words.txt to the bucket
#gsutil cp input_words.txt gs://flex_templates_my_pipeline/input_words.txt

export ARTIFACT_REGISTRY_REPO="webscraper-pipeline"
export PROJECT_ID=$(gcloud config get-value project)
export FLEX_BUCKET="flex_templates_my_pipeline"
export TEMPLATE_FILE="webscraper_template.json"
# create artifact registry
echo "Create Artifact Registry"
gcloud artifacts repositories create ${ARTIFACT_REGISTRY_REPO} \
--repository-format=docker \
--location=europe-west2 \
--description="Artifact Registry for the webscraper pipeline"
# docker image

echo "Build Docker image"
docker build --no-cache -t webscraper_pipeline -f docker/Dockerfile .
echo "Tag Docker image"
docker tag webscraper_pipeline europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/webscraper_pipeline:latest
echo "Push Docker image"
docker push europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/webscraper_pipeline:latest

# flex template

if ! gsutil ls -p ${PROJECT_ID} gs://${FLEX_BUCKET} &> /dev/null;
    then
        echo creating gs://${FLEX_BUCKET} ... ;
        gcloud storage buckets create gs://${FLEX_BUCKET} --location eu;
        sleep 5;
    else
        echo "Bucket ${FLEX_BUCKET} already exists!"
fi

echo "Build Flex Template"
gcloud dataflow flex-template build gs://${FLEX_BUCKET}/${TEMPLATE_FILE} \
--image-gcr-path europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/webscraper_pipeline:latest \
--sdk-language "PYTHON" \
--metadata-file metadata/metadata.json \
--project ${PROJECT_ID} \
--worker-region europe-west2 \
--env  "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt" \
--env "FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline/pipeline.py" \
--env "FLEX_TEMPLATE_PYTHON_SETUP_FILE=setup.py" \
--flex-template-base-image "PYTHON3" \
--py-path "."