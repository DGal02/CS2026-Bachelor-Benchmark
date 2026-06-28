#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE="docker compose -f $SCRIPT_DIR/docker-compose.yml"
export SYSTEM="redis"
HOST_SYSTEM="wsl"
MAX_CPUS_LIST="1 2"

$COMPOSE build app

for max_cpus in $MAX_CPUS_LIST; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Starting: system=$SYSTEM, MAX_CPUS=$max_cpus ==="

    TEST_RESULT_FOLDER=$(date '+%Y-%m-%d-%H-%M-%S')
    export TEST_RESULT_FOLDER

    $COMPOSE up -d app
    MAX_CPUS="$max_cpus" $COMPOSE up -d "$SYSTEM"

    sh "$SCRIPT_DIR/run_tests.sh"

    result_dir="$SCRIPT_DIR/../testResult/$TEST_RESULT_FOLDER"
    cat > "$result_dir/metadata.json" << EOF
{
  "system": "$SYSTEM",
  "max_cpus": $max_cpus,
  "host_system": "$HOST_SYSTEM"
}
EOF

    $COMPOSE down

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Done: MAX_CPUS=$max_cpus, folder=$TEST_RESULT_FOLDER ==="
done