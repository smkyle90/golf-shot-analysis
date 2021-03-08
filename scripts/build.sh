#!/bin/bash
# This script is not meant to be called directly. Use the Makefile included.

# Exit on any error
set -e

IMAGE_NAME=$1
IMAGE_TAG=$2

# Check for args
if [ -z ${IMAGE_NAME} ]; then
  echo "Usage: ./build.sh IMAGE_NAME IMAGE_TAG"
  echo "exit 1"
  exit 1
fi


if [ -z ${IMAGE_TAG} ]; then
  echo "Usage: ./build.sh IMAGE_NAME IMAGE_TAG"
  echo "exit 1"
  exit 1
fi

echo "Building:    ${IMAGE_NAME}:${IMAGE_TAG}"

sudo docker build --progress plain \
    -t $IMAGE_NAME:$IMAGE_TAG \
    -f Dockerfile .
