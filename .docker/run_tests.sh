#!/bin/sh
set -e

TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')

PROCESS_COUNTS="1 2 4 8"
ITERATIONS_LIST="10000 100000 1000000"
DATA_SIZES="small medium"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting tests: folder=$TEST_RESULT_FOLDER"

for data_size in $DATA_SIZES; do
    for iterations in $ITERATIONS_LIST; do
        if [ "$data_size" = "medium" ] && [ "$iterations" = "1000000" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skipping: data_size=$data_size, iterations=$iterations"
            continue
        fi

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: data_size=$data_size, iterations=$iterations"

        for count in $PROCESS_COUNTS; do
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting test run with $count process(es)..."

            pids=""
            i=0
            while [ $i -lt $count ]; do
                docker exec \
                  -e TEST_RESULT_FOLDER="$TEST_RESULT_FOLDER" \
                  -e ITERATIONS="$iterations" \
                  -e DATA_SIZE="$data_size" \
                  -e MAX_WORKERS="$count" \
                  -e PROCESS_INDEX="$i" \
                  magisterka-app python benchmark/redis-test.py &
                pids="$pids $!"
                i=$((i + 1))
            done

            wait $pids
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] All $count process(es) finished."
        done
    done
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] All tests completed."