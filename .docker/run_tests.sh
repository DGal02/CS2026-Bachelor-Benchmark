#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULT_DIR="$SCRIPT_DIR/../testResult/$TEST_RESULT_FOLDER"

# CHOICES
#PROCESS_COUNTS="1 2 4 8"
#ITERATIONS_LIST="10000 100000 1000000"
#DATA_SIZES="small medium"
#CATEGORIES="insert read update delete mix queue doc_insert doc_read doc_read_partial doc_update_partial doc_increment doc_delete"
# END OF CHOICES

PROCESS_COUNTS="1"
ITERATIONS_LIST="10000"
DATA_SIZES="small"
CATEGORIES="insert read update delete mix queue doc_insert doc_read doc_read_partial doc_update_partial doc_increment doc_delete"
FIXED_CATEGORIES="queue doc_insert doc_read doc_read_partial doc_update_partial doc_increment doc_delete"

contains() {
    for item in $1; do
        [ "$item" = "$2" ] && return 0
    done
    return 1
}

run_test() {
    category=$1
    data_size=$2
    iterations=$3
    count=$4

    stats_dir="$RESULT_DIR/$data_size/$iterations/workers-$count"
    mkdir -p "$stats_dir"

    echo "timestamp,container,cpu_perc,mem_usage" > "$stats_dir/stats.csv"
    while true; do
        ts=$(date '+%Y-%m-%d %H:%M:%S')
        docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" python-app "system-$SYSTEM" 2>/dev/null | while IFS= read -r line; do
            echo "$ts,$line"
        done >> "$stats_dir/stats.csv"
        sleep 0.2
    done &
    monitor_pid=$!

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
          python-app python "benchmark/${SYSTEM}_test.py" &
        pids="$pids $!"
        i=$((i + 1))
    done

    wait $pids
    kill "$monitor_pid" 2>/dev/null || true
}

run_category() {
    category=$1
    data_size=$2
    iterations=$3

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Category: $category"

    for count in $PROCESS_COUNTS; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting test run with $count process(es)..."
        run_test "$category" "$data_size" "$iterations" "$count"
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
            contains "$FIXED_CATEGORIES" "$category" && continue
            run_category "$category" "$data_size" "$iterations"
        done
    done

    for category in $FIXED_CATEGORIES; do
        contains "$CATEGORIES" "$category" && run_category "$category" "$data_size" "0"
    done
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] All tests completed."