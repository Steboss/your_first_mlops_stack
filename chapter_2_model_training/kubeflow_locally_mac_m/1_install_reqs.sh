#!/bin/bash 

echo "Installing requirements"
brew install k3d 
docker pull docker.io/rancher/k3s:v1.28.8-k3s1
brew install k9s 
brew install txn2/tap/kubefwd
echo "Creating a k3d cluster"
k3d cluster create localkfp -a 1 -s 1 --servers-memory 8Gb
