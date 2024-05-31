#!/bin/bash

# run the code
python create_fake_dataset.py

# copy the file to the bucket
gsutil cp fake_dataset.csv gs://vertexai_inputfiles/fake_dataset.csv

# create a table from the file
bq load --source_format=CSV --autodetect learning_vertexai.fake_dataset_1  gs://vertexai_inputfiles/fake_dataset.csv

