#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE="docker compose -f $SCRIPT_DIR/docker-compose.yml"
#SYSTEM: redis memcached leveldb
export SYSTEM="leveldb"

export EMBEDDED_SYSTEMS="leveldb rocksdb berkeleydb"

is_embedded() {
    for item in $EMBEDDED_SYSTEMS; do
        [ "$item" = "$SYSTEM" ] && return 0
    done
    return 1
}
#HOST_SYSTEM="wsl"
HOST_SYSTEM="wsl"
#MAX_CPUS_LIST="1 2 4"
MAX_CPUS_LIST="1 2 4"

for max_cpus in $MAX_CPUS_LIST; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Starting: system=$SYSTEM, MAX_CPUS=$max_cpus ==="

    TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')
    export TEST_RESULT_FOLDER

    export MAX_CPUS="$max_cpus"
    if is_embedded; then
        export APP_CPUS="$max_cpus"
    fi
    $COMPOSE build app
    $COMPOSE up -d app
    is_embedded || $COMPOSE up -d "$SYSTEM"

    sleep 5
    sh "$SCRIPT_DIR/run_tests.sh"

    result_dir="$SCRIPT_DIR/../testResult/$TEST_RESULT_FOLDER"
    cat > "$result_dir/metadata.json" << EOF
{
  "system": "$SYSTEM",
  "max_cpus": $max_cpus,
  "host_system": "$HOST_SYSTEM"
}
EOF

    sleep 5
    $COMPOSE down

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Done: MAX_CPUS=$max_cpus, folder=$TEST_RESULT_FOLDER ==="
done