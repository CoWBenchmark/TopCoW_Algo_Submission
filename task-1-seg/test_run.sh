#!/usr/bin/env bash

# Stop at first error
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOCKER_TAG="algo_docker_task-1_seg"
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
echo "##### Test 0 >>> segmentation mask check"
# Compare the segmentation output from Docker with the expected segmentation mask
# TODO: Provide the expected output segmentation mask of your algorithm in ./test/expected_output/
# TODO: In the python code snippet below change the following if necessary:

IMAGE_FILENAME="output.mha"
EXPECTED_SEG_MASK="expected_output_dummy_mra.mha"

echo "TODO: change IMAGE_FILENAME and EXPECTED_SEG_MASK if needed"

docker run --rm \
        --volume "$OUTPUT_DIR":/output \
        --volume $SCRIPT_DIR/test/expected_output/:/expected_output/ \
        biocontainers/simpleitk:v1.0.1-3-deb-py3_cv1 python3 -c """
import os
import SimpleITK as sitk

output_path = '/output/images/cow-multiclass-segmentation/${IMAGE_FILENAME}'
print(f'{output_path} isfile? ', os.path.isfile(output_path))
expected_output_path = '/expected_output/${EXPECTED_SEG_MASK}'
print(f'{expected_output_path} isfile? ', os.path.isfile(expected_output_path))

output = sitk.ReadImage(output_path)
expected_output = sitk.ReadImage(expected_output_path) 

label_filter = sitk.LabelOverlapMeasuresImageFilter()
label_filter.Execute(output, expected_output)
dice_score = label_filter.GetDiceCoefficient()

print(f'dice_score = {dice_score}')

if dice_score == 1.0:
    print('[Success] Dice score=1, Test 0 passed!')
else:
    print('Dice score != 1, Test 0 failed!')
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
