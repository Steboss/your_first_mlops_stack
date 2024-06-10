#!/bin/bash

# install
pip3 install -r requirements.txt

# run the code
python3 generate_data.py

# copy the file to the bucket
gsutil cp fake_dataset.csv gs://vertexai_inputfiles/fake_dataset.csv


bq --location=EU mk -d \
    --default_table_expiration 36000 \
    --description "VertexAI dataset" \
    learning_vertexai
# create a table from the file
bq load --source_format=CSV --autodetect learning_vertexai.fake_dataset_1  gs://vertexai_inputfiles/fake_dataset.csv

