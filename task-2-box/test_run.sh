#!/usr/bin/env bash

# Stop at first error
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOCKER_TAG="algo_docker_task-2_box"
DOCKER_NOOP_VOLUME="${DOCKER_TAG}-volume"

INPUT_DIR="${SCRIPT_DIR}/test/input"
OUTPUT_DIR="${SCRIPT_DIR}/test/output"


echo "=+= Cleaning up any earlier output"
if [ -d "$OUTPUT_DIR" ]; then
  # Ensure permissions are setup correctly
  # This allows for the Docker user to write to this location
  rm -rf "${OUTPUT_DIR}"/*
  chmod -f o+rwx "$OUTPUT_DIR"
else
  mkdir -m o+rwx "$OUTPUT_DIR"
fi


echo "=+= (Re)build the container"
docker build "$SCRIPT_DIR" \
  --platform=linux/amd64 \
  --tag $DOCKER_TAG 2>&1


echo "=+= Doing a forward pass"
## Note the extra arguments that are passed here:
# '--network none'
#    entails there is no internet connection
# 'gpus all'
#    enables access to any GPUs present
# '--volume <NAME>:/tmp'
#   is added because on Grand Challenge this directory cannot be used to store permanent files
docker volume create "$DOCKER_NOOP_VOLUME" > /dev/null
docker run --rm \
    --platform=linux/amd64 \
    --network none \
    --gpus all \
    --volume "$INPUT_DIR":/input:ro \
    --volume "$OUTPUT_DIR":/output \
    --volume "$DOCKER_NOOP_VOLUME":/tmp \
    $DOCKER_TAG
docker volume rm "$DOCKER_NOOP_VOLUME" > /dev/null

# Ensure permissions are set correctly on the output
# This allows the host user (e.g. you) to access and handle these files
docker run --rm \
    --quiet \
    --env HOST_UID=`id --user` \
    --env HOST_GID=`id --group` \
    --volume "$OUTPUT_DIR":/output \
    alpine:latest \
    /bin/sh -c 'chown -R ${HOST_UID}:${HOST_GID} /output'

echo "=+= Wrote results to ${OUTPUT_DIR}"

###################################################################################
# Test if the docker outputs match the expected outputs in ./test/expected_output/
###################################################################################

echo "#################################################"
echo "##### Test 0 >>> bounding box check"
# Compare the bounding box output from Docker with the expected bounding box

docker run --rm \
  --volume "$OUTPUT_DIR":/output \
  --volume $SCRIPT_DIR/test/expected_output/:/expected_output/ \
  python:3.10-slim python -c """
import json
import os

output_path = '/output/cow-roi.json'
print(f'{output_path} isfile? ', os.path.isfile(output_path))
expected_output_path = '/expected_output/cow-roi.json'
print(f'{expected_output_path} isfile? ', os.path.isfile(expected_output_path))

with open(output_path, 'r') as f:
    output = json.load(f)
with open(expected_output_path, 'r') as f:
    expected_output = json.load(f)

are_equal = output == expected_output

if are_equal:
    print('[Success] The cow-roi dictionaries are equal, Test 0 passed!')
else:
    print('The cow-roi dictionaries are not equal, Test 0 failed!')
    print('[FAIL] Test 0 has FAILED!')
"""
echo "#################################################"
echo

echo "#################################################"
echo "##### Test 1 >>> /output/ folder check"
echo -e "\n$ ls -alR /output/ \n"

docker run --rm \
        --volume "$OUTPUT_DIR":/output \
        python:3.10-slim ls -alR /output/

echo "#################################################"
echo

echo "Please make sure you pass the above 2 tests before submitting your docker"

echo -e "\n=+= Save this image for uploading via save.sh \"${DOCKER_TAG}\""
