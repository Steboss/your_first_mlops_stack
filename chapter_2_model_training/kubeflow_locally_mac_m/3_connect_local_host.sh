#!/bin/bash 

echo "You'll be now able to access to KFP at http://ml-pipeline-ui:80"
sudo kubefwd svc -n kubeflow
