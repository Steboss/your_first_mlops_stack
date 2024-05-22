#!/bin/bash

export DOCKER_USER=$(docker-credential-$(jq -r .credsStore ~/.docker/config.json) list | jq -r '
  . |
  to_entries[] |
  select(.key | contains("docker.io")) |
  .value
' | sort -u | head -n 1)


docker build -t ${DOCKER_USER}/iris-processor:latest -f docker/Dockerfile .
docker push ${DOCKER_USER}/iris-processor:latest
