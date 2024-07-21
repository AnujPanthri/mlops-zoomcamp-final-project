#!/bin/bash

function exit_script() {
    EXIT_CODE=$?
    if [ ${EXIT_CODE} != 0 ];then
        echo "EXIT_CODE: $EXIT_CODE"
        docker compose logs
        docker compose down
        exit ${EXIT_CODE}
    fi
}

function check_service_heath(){
    interval=2
    max_tries=10
    echo "Checking service health:"
    for ((i=1 ; i<=$max_tries ; i++ )); do
        echo "trial $i out of $max_tries"
        status_code=$(curl -o /dev/null -s -w "%{http_code}" --max-time $interval http://localhost:8080/);
        echo "status_code: $status_code";
        if [ "$status_code" -eq 200 ]; then
            echo "service is healthy";
            return;
        else
            echo "failed, retrying is $interval seconds...";
            sleep $interval
        fi
    done
    exit 1
}

# don't exit if a command exits with an exit code non-zero
set +e

# cd to the parent dir of current dir
cd "$(dirname "$0")/.."

export DOWLOAD_MODEL_FLAG="false"
export MODEL_DIR="integration-tests/model/"
export LOG_TO_DB_FLAG="false"
docker compose up deployment --no-deps --build -d
exit_script


check_service_heath
exit_script

python integration-tests/test_model.py
exit_script

# finally close everything and exit
docker compose down
EXIT_CODE=$?
exit ${EXIT_CODE}
