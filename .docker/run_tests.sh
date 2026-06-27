#!/bin/sh
set -e

TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')
ITERATIONS=${ITERATIONS:-10000}
DATA_SIZE=${DATA_SIZE:-small}

echo "Starting tests: folder=$TEST_RESULT_FOLDER, iterations=$ITERATIONS, data_size=$DATA_SIZE"

docker exec \
  -e TEST_RESULT_FOLDER="$TEST_RESULT_FOLDER" \
  -e ITERATIONS="$ITERATIONS" \
  -e DATA_SIZE="$DATA_SIZE" \
  magisterka-app python benchmark/redis-test.py