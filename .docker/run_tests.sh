#!/bin/sh
set -e

TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')
ITERATIONS=${ITERATIONS:-10000}
DATA_SIZE=${DATA_SIZE:-small}

PROCESS_COUNTS="1 2"

echo "Starting tests: folder=$TEST_RESULT_FOLDER, iterations=$ITERATIONS, data_size=$DATA_SIZE"

for count in $PROCESS_COUNTS; do
    echo "Starting test run with $count process(es)..."

    pids=""
    i=0
    while [ $i -lt $count ]; do
        docker exec \
          -e TEST_RESULT_FOLDER="$TEST_RESULT_FOLDER" \
          -e ITERATIONS="$ITERATIONS" \
          -e DATA_SIZE="$DATA_SIZE" \
          -e MAX_WORKERS="$count" \
          -e PROCESS_INDEX="$i" \
          magisterka-app python benchmark/redis-test.py &
        pids="$pids $!"
        i=$((i + 1))
    done

    wait $pids
    echo "All $count process(es) finished."
done