#!/bin/sh

# remove the man-db
sudo apt-get remove -y --purge man-db
#
echo "Install pip"
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
# Install GCP storage
echo "pip3 install google-cloud-storage"
python3 -m pip install google-cloud-storage

# Install mlflow
echo "pip3 install mlflow"
python3 -m pip install mlflow
# add the mlflow bins to the path
export PATH=$PATH:~/.local/bin
echo "MLflow version"
mlflow --version

echo "Installing SQLite3..."
sudo apt-get install sqlite3

echo "Sqlite3 installed"
echo "Sqlite version"
sqlite3 --version

echo "Setting up ip"
internalIp=$(hostname -i)
echo "Internal IP = ${internalIp}"

echo "Spin up the MLflow server"
mlflow server --backend-store-uri sqlite:///mlruns.db  --default-artifact-root gs://mlflowartifactsbucket/artifacts --host $internalIp