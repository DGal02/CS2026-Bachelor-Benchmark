#!/bin/sh
set -e

TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')

PROCESS_COUNTS="1 2 4 8"
ITERATIONS_LIST="10000 100000 1000000"
DATA_SIZES="small medium"
CATEGORIES="insert read update delete mix"

run_category() {
    category=$1
    data_size=$2
    iterations=$3

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Category: $category"

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
              -e TEST_CATEGORY="$category" \
              magisterka-app python benchmark/redis_test.py &
            pids="$pids $!"
            i=$((i + 1))
        done

        wait $pids
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] All $count process(es) finished."
    done
}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting tests: folder=$TEST_RESULT_FOLDER"

for data_size in $DATA_SIZES; do
    for iterations in $ITERATIONS_LIST; do
        if [ "$data_size" = "medium" ] && [ "$iterations" = "1000000" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skipping: data_size=$data_size, iterations=$iterations"
            continue
        fi

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: data_size=$data_size, iterations=$iterations"

        for category in $CATEGORIES; do
            run_category "$category" "$data_size" "$iterations"
        done
    done

    run_category "queue" "$data_size" "0"
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] All tests completed."