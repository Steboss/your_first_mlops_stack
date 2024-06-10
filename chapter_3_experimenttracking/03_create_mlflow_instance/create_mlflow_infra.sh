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
gcloud compute instances create mlflow-server \
    --project=${PROJECT_ID} \
    --zone=europe-west2-b \
    --machine-type=e2-medium \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --can-ip-forward \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --metadata=startup-script=\#\!/bin/sh$'\n'$'\n'\#\ \
remove\ the\ man-db$'\n'sudo\ apt-get\ remove\ -y\ \
    --purge\ \
man-db$'\n'\#$'\n'echo\ \"Install\ pip\"$'\n'curl\ https://bootstrap.pypa.io/get-pip.py\ -o\ get-pip.py$'\n'python3\ get-pip.py$'\n'\#\ Install\ GCP\ storage$'\n'echo\ \"pip3\ install\ google-cloud-storage\"$'\n'python3\ -m\ pip\ install\ google-cloud-storage$'\n'$'\n'\#\ Install\ mlflow$'\n'echo\ \"pip3\ install\ mlflow\"$'\n'python3\ -m\ pip\ install\ mlflow$'\n'\#\ add\ the\ mlflow\ bins\ to\ the\ path$'\n'export\ PATH=\$PATH:\~/.local/bin$'\n'echo\ \"MLflow\ version\"$'\n'mlflow\ \
    --version$'\n'$'\n'echo\ \
\"Installing\ SQLite3...\"$'\n'sudo\ apt-get\ install\ sqlite3$'\n'$'\n'echo\ \"Sqlite3\ installed\"$'\n'echo\ \"Sqlite\ version\"$'\n'sqlite3\ \
    --version$'\n'$'\n'echo\ \
\"Setting\ up\ ip\"$'\n'internalIp=\$\(hostname\ -i\)$'\n'echo\ \"Internal\ IP\ =\ \$\{internalIp\}\"$'\n'$'\n'echo\ \"Spin\ up\ the\ MLflow\ server\"$'\n'mlflow\ server\ \
    --backend-store-uri\ \
sqlite:///mlruns.db\ \ \
    --default-artifact-root\ \
gs://mlflowartifactsbucket/artifacts\ \
    --host\ \
\$internalIp \
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
    --reservation-affinity=any

# Create a network rule
gcloud compute --project=${PROJECT_ID} firewall-rules create mlflow-server \
        --direction=INGRESS \
        --priority=999 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:5000 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=mlflow-server