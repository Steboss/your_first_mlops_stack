#!/bin/bash

# copy the file to the bucket
gsutil cp iris.csv gs://vertexai_inputfiles/iris.csv

bq --location=EU mk -d \
    --default_table_expiration 36000 \
    --description "VertexAI dataset" \
    learning_vertexai
# create a table from the file
bq load --source_format=CSV --autodetect learning_vertexai.iris_dataset  gs://vertexai_inputfiles/iris.csv

