#!/bin/bash

export ARTIFACT_REGISTRY_REPO="randomforest-vertexai-mlflow"
export PROJECT_ID=$(gcloud config get-value project)

gcloud artifacts repositories create ${ARTIFACT_REGISTRY_REPO} \
    --repository-format=docker \
    --location=europe-west2 \
    --description="Repo for vertexAI models with MLflow" \
    --async


echo "Build Docker image"
docker build --no-cache -t randomforest_vertexai_mlflow -f docker/Dockerfile .
echo "Tag Docker image"
docker tag randomforest_vertexai_mlflow europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/randomforest_vertexai_mlflow:latest
echo "Push Docker image"
gcloud auth configure-docker europe-west2-docker.pkg.dev
docker push europe-west2-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/randomforest_vertexai_mlflow:latest
