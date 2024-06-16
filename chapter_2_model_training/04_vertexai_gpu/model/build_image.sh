#!/bin/bash

export ARTIFACT_REGISTRY_REPO="model-gpu-vertexai"
export PROJECT_ID=$(gcloud config get-value project)

gcloud artifacts repositories create ${ARTIFACT_REGISTRY_REPO} \
    --repository-format=docker \
    --location=europe-west2 \
    --description="Repo for vertexAI models" \
    --async


echo "Build Docker image"
docker build --no-cache -t model_gpu -f docker/Dockerfile .
echo "Tag Docker image"
docker tag model_gpu europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/model_gpu:latest
echo "Push Docker image"
gcloud auth configure-docker europe-west2-docker.pkg.dev
docker push europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/model_gpu:latest
