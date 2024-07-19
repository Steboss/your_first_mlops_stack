#!/bin/bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
export MLFLOW_BUCKET="mlflowartifactbucket"

# Create the MLflow bucket
gsutil mb gs://mlflowartifactsbucket
if ! gsutil ls -p ${PROJECT_ID} gs://${MLFLOW_BUCKET} &> /dev/null;
    then
        echo creating gs://${MLFLOW_BUCKET} ... ;
        gcloud storage buckets create gs://${MLFLOW_BUCKET} --location eu;
        sleep 5;
    else
        echo "Bucket ${MLFLOW_BUCKET} already exists!"
fi

# Create the MLflow instance
gcloud compute instances create mlflow-server2 \
    --project=${PROJECT_ID} \
    --zone=europe-west2-b \
    --machine-type=e2-medium \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --can-ip-forward \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=mlflow-server,http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=mlflow-server,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240607,mode=rw,size=10,type=projects/data-gearbox-421420/zones/europe-west2-b/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any \
    --metadata=startup-script='#!/bin/sh
sudo apt-get remove -y --purge man-db
pip3 install --upgrade pip
sudo apt-get -y remove python3-blinker
pip3 uninstall -y blinker
pip3 install blinker==1.8.2
echo "pip3 install google-cloud-storage"
pip3 install google-cloud-storage
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
echo "Internal IP = ${internalIp}
EOF'

# Create a network rule
gcloud compute --project=${PROJECT_ID} firewall-rules create mlflow-server2 \
        --direction=INGRESS \
        --priority=999 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:5000 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=mlflow-server