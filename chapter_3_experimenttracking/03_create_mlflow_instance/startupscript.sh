#!/bin/sh

# remove the man-db
sudo apt-get remove -y --purge man-db
pip3 install --upgrade pip
# fix blinker
sudo apt-get -y remove python3-blinker
pip3 uninstall -y blinker
pip3 install blinker==1.8.2
# Install GCP storage
echo "pip3 install google-cloud-storage"
pip3 install google-cloud-storage
# Install mlflow
echo "pip3 install mlflow"
sudo pip3 install mlflow
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