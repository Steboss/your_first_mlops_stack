#!/bin/bash

export ARTIFACT_REGISTRY_REPO="randomforest-vertexai"
export PROJECT_ID=$(gcloud config get-value project)

gcloud artifacts repositories create ${ARTIFACT_REGISTSRY_REPO} \
    --repository-format=apt \
    --location=europe-west2 \
    --description="Repo for vertexAI models" \
    --async


echo "Build Docker image"
docker build --no-cache -t randomforest_vertexai -f docker/Dockerfile .
echo "Tag Docker image"
docker tag randomforest_vertexai europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/randomforest_vertexai:latest
echo "Push Docker image"
gcloud auth configure-docker
docker push europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/randomforest_vertexai:latest
