import kfp
from kfp.v2 import compiler
from kfp.v2.dsl import component
from google.cloud.aiplatform import pipeline_jobs
from typing import Optional, NamedTuple
from pathlib import Path
import yaml
import json


@component(
    packages_to_install=[
        "google_cloud_core",
        "google_cloud_aiplatform",
        "datetime",
    ]
)
def train_model(
    artifacts_bucket: str,
    project_id: str,
    location: str,
    model_image: str,
    machine_type: Optional[str] = "n1-standard-4",
    accelerator_type: Optional[str] = "ACCELERATOR_TYPE_UNSPECIFIED",
    replica_count: Optional[int] = 1,
    accelerator_count: Optional[int] = None,
    training_job_name: Optional[str] = None,
    model_display_name: Optional[str] = None,
    training_args: Optional[list] = None,
    model_serving_uri: Optional[str] = None,
    after_component: Optional[str] = None,
) -> str:
    r"""This function train a given model with CustomContainerTrainingJob.
    The function return the model path:
    (e.g."projects/{service_account_number}/locations/{project_region}/models/{input_model})

    Args
    ----------
        artifacts_bucket: str, where artifacts are saved
        project_id: str, GCP project
        project_region: str, location/project region
        model_image: str, GCR path for the model image
        machine_type: Optional(str), define the machine type to run the training e.g. n1-standard-4
        accelerator_type: Optional(str), NVIDIA_TESLA_K80, NVIDIA_TESLA_P100 etc
        replica_count: Optional(int) the number of worker replicas
        accelerator_count: Optional(int) the number of accelerator to be used
        training_job_name: Optional or string name for the training job, if not given a custom name will be created
        model_display_name: Optional or str, name of the final model to be given if model_serving_uri is given
        training_args: Optional or str, possible training arguments for model
        model_serving_uri: Optional or str, uri for the model endpoint serving API on eu.gcr
        after_component: This is an optional input and can be of any type,
                        if the component has to be execute sequentially in general

    Returns
    ------
        model.resource_name: aiplatform.Model, return the resource path of the model.
                            This is needed for deploying models as vertexAI endpoints
        job.resource_name: str, return the path of the trained algorithm
    """
    from google.cloud import aiplatform
    from datetime import datetime
    import os
    import logging

    logging.getLogger().setLevel(logging.INFO)
    # the project number is needed for the network path
    project_number = os.environ["CLOUD_ML_PROJECT_ID"]
    logging.info(f"Project {project_number}")
    network_path = f"projects/{project_number}/global/networks/default"
    # initialize the aiplatform Client
    aiplatform.init(
        project=project_id, location=location, staging_bucket=artifacts_bucket
    )

    if not training_job_name:
        training_job_name = "training_" + datetime.today().strftime("%Y-%m-%d_%H:%M:%S")

    # define the bigquery destination, namely where the input data will be saved in BQuery by VAI
    bigquery_destination = "bq://" + project_id

    # set up the CustomContainerTrainingJob
    # if model_serving_uri is not given model_serving arguments are ignored by the API
    job = aiplatform.CustomContainerTrainingJob(
        display_name=training_job_name,
        container_uri=model_image,
        model_serving_container_image_uri=model_serving_uri,
        model_serving_container_predict_route="/predict",
        model_serving_container_health_route="/health_check",
        model_serving_container_ports=[8080],
    )
    # run the training bit
    model = job.run(
        dataset=None,
        model_display_name=model_display_name,
        args=training_args,
        replica_count=replica_count,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        base_output_dir="gs://" + artifacts_bucket,
        bigquery_destination=bigquery_destination,
        network=network_path,
    )

    if model:
        # in this case we have a model
        model.resource_name
    else:
        # otherwise return where artefacts have been saved
        return "gs://" + artifacts_bucket + "/model"


@component()
def preprocess_info() -> NamedTuple("Data",[("training_job_name", str),("training_args", list),]):
    """ This component prepare all the inputs for the training job

    The function returns the training job name for the model, so it can be
    updated every day. It also returns the training arguments for the model.
    This can be useful if we want to use a daily dataset

    Return
    ------
        NamedTuple: `Data` as two keys:
                    `training_job_name`: the name of the training job and
                    `training_args` the training arguments.
    """
    import datetime
    from collections import namedtuple

    today = datetime.datetime.utcnow().isoformat()
    training_job_name = f"scamspam-{today}"

    # here is where our data is outputted from the bigquery component
    training_args = ["gs://bucket/path"]
    # output is read as a namedtuple
    output_tuple = namedtuple(
        "Data",
        [
            "training_job_name",
            "training_args",
        ],
    )

    return output_tuple(training_job_name, training_args)


@kfp.dsl.pipeline(name="rf-example-1", description="Example for running a RF model")
def pipeline(
    project_id: str,
    vertex_project: str,
    project_region: str,
    vertex_bucket: str,
    cache: bool,
    input_data_path: str,
    container_image: str,
    artefacts_bucket: str,
):
    r"""Main KFP pipeline.

    The pipeline retrieves data from BQ and then it launches a RF model

    Args:
    -----
        project_id: str, gcp project id
        vertex_project: str, vertex project id
        project_region: str, project region
        vertex_bucket: str, vertex bucket
        cache: bool, cache
        input_data_path: str, input data path
        container_image: str, model image on the Artifact Registry
        artefacts_bucket: str, where we want to save model and artefacts bucket
    """
    preprocess_output = preprocess_info()
    # query the dataset and export it
    sql_query = (
        "SELECT * FROM trustedplatform-pl-staging.fake_dataset.classification_test"
    )

    dataset = bigquery.read_from_bq(
        sql_query=sql_query,
        project_id=vertex_project,
        save_results=True,
        user_output_data_path=input_data_path,
        output_data_format="csv",
    )

    training_status = train_model.train_model(
        artifacts_bucket=artefacts_bucket,
        project_id=vertex_project,
        location=project_region,
        model_image=container_image,
        training_job_name=preprocess_output.outputs["training_job_name"],
        training_args=preprocess_output.outputs["training_args"],
        after_component=dataset.output,
    )


if __name__ == "__main__":
    package_path = "pipeline.json"
    config = yaml.safe_load(Path("vertex_config.yaml").read_text())
    pipe = compiler.Compiler().compile(pipeline_func=pipeline, package_path=package_path)
    with open(package_path, "r") as ifile:
         pipeline_specs = json.load(ifile)
    display_name = pipeline_specs["pipelineSpec"]["pipelineInfo"]["name"]
    pipeline = pipeline_jobs.PipelineJob(
            display_name,
            package_path,
            pipeline_root=config["vertex_bucket"],
            parameter_values=config,
            enable_caching=bool(config["cache"]),
            project=config["project_id"] if not project_vertex else project_vertex,
            location=config["project_region"],
        )
    pipeline.submit()
