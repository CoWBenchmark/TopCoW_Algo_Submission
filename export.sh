#!/usr/bin/env bash

bash ./build.sh

date_suffix=$(date +"%b%d_%H%M")

docker save cowsegmentation | gzip -c > algo_docker_${date_suffix}.tar.gz
