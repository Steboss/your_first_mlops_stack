### KFP pipeline in VertexAI

This example runs a pipeline in VertexAI

#### 1. Open the GCP shell

Activate the GCP Shell in your GCP project:

![Activate Shell](imgs/ActivateShell.png)

#### 2. Prepare the input data

We are going to create the input data for the tutorial. These data are made through `sklearn` as a fake dataset:
```bash
bash prepare_data/create_bqtable.sh
```

The script will run `prepare_data/generate_data.py`. The generated dataset will be copied on BigQuery so we'll have a dataset and a table to be used.

#### 3. Create the model image

Again we need to containerized our model:
```bash
bash model/build_image.sh
```
The script will generate the image in `randomforest-vertexai` repository. In this way, we'll use `randomforest-vertexai/randomforest_vertexai:latest` in our KFP pipeline


#### 4. Run the KFP pipeline

Now that data and image are done, we can run the pipeline:
```bash
python pipeline/pipeline.py
```

The pipeline reads the input arguments from `pipeline/config.yaml` file. You'll have to substitute some values, to make it work on your GCP project:

```yaml
project_region: europe-west2
vertex_project: CHANGE_THIS_TO_YOUR_PROJECT_ID
vertex_bucket: gs://vertexai_inputfiles
cache: False
input_data_path: gs://vertexai_inputfiles/poc_table
container_image: europe-west2-docker.pkg.dev/YOUR_PROJECT_ID/randomforest-vertexai/randomforest_vertexai
location: europe-west2-b
# this must be created within europe-west2
artefacts_bucket: vertexai_output_models
project_id: CHANGE_THIS_TO_YOUR_PROJECT_ID
```
In particular, you'll have to change `vertex_project`, `container_image` and `project_id`.
