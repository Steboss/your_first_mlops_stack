import os
import typer
from pathlib import Path
from google.cloud import storage
from urllib.parse import urlparse, urljoin, ParseResult
import pandas as pd
import joblib

# gcs
import fsspec
import gcsfs

# metrics
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import logging

logging.getLogger().setLevel(logging.INFO)

# HELPER FUNCTIONS
def copy_local_directory_to_gcs(local_path: Path, output_bucket: str, gcs_path: Path):
    """Copy the input data to local machine

    Args
    ---------
        local_path: Path, local path where the artefacts are saved
        output_bucket: str, gcs bucket where we want to save the artefacts to
        gcs_path: str, path in the bucket to save artefacts
    """
    storage_client = storage.Client("trustedplatform-pl-staging")
    bucket = storage_client.get_bucket(output_bucket)

    remote_path = f"{gcs_path}/model.joblib"
    logging.info(remote_path)
    blob = bucket.blob(str(remote_path))
    blob.upload_from_filename(local_path)


def load_data(data_path):
    r"""Load data from a bucket to local mode

    Args
    ---------
        data_path: str, input path where the data to be read are stored

    Returns
    ---------
        pandas dataframe: read data are stored in a pandas dataframe
    """
    logging.info(f"Data parsing {data_path}")
    data_path_as_url = urlparse(data_path)
    if data_path_as_url.scheme == "gs":
        dataset_location_path = urljoin(data_path_as_url.path, "poc_table") # GIVE A NAME TO THE TALBE
        dataset_location_url = ParseResult(
            scheme=data_path_as_url.scheme,
            netloc=data_path_as_url.netloc,
            path=dataset_location_path,
            params=data_path_as_url.params,
            query=data_path_as_url.query,
            fragment=data_path_as_url.fragment,
        )
        dataset_location = dataset_location_url.geturl()
    else:
        data_location = Path(data_path)
        dataset_location = data_location / "poc_table"
    logging.info(f"Local data {dataset_location}")

    return pd.read_csv(dataset_location)


def main(data_path: str):
    r"""Main model function to train a random forest model

    Args:
        data_path: str, input path where the data are stored
    """
    logging.info("Loading data...")
    df = load_data(data_path)
    logging.info("Preparing X and y")
    y = df["target"]
    X = df.drop(labels=["target"], axis=1)

    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # create output directory
    output_folder = os.getcwd() + "/outputs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Random Forest
    clf = RandomForestClassifier(n_estimators=2)

    params = {"X": X_train, "y": y_train}

    clf.fit(**params)
    # save the model
    joblib.dump(clf, f"{output_folder}/model.joblib")
    logging.info("Saving model")
    # Copy data to bucket
    copy_local_directory_to_gcs(
        f"{output_folder}/model.joblib",
        "vertexai_output_models",
        "RandomForestModel",
    )


if __name__ == "__main__":
    typer.run(main)
