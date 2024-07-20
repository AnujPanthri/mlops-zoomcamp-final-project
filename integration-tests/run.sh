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


# don't exit if a command exits with an exit code non-zero
set +e

# cd to the parent dir of current dir
cd "$(dirname "$0")"

export DOWLOAD_MODEL_FLAG="false"
export MODEL_DIR="integration-tests/model/"
export LOG_TO_DB_FLAG="false"
docker compose up --build -d
exit_script

sleep 10
python test_model.py
exit_script

# finally close everything and exit
docker compose down
EXIT_CODE=$?
exit ${EXIT_CODE}
