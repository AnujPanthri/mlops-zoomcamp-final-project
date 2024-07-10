### entrypoint.sh
#!/bin/bash

set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "  Creating user and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        CREATE USER $database WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';
        GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
        ALTER DATABASE $database OWNER TO $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    export PGPASSWORD=$POSTGRES_PASSWORD
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    echo "using username '$POSTGRES_USER'"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done
    echo "Multiple databases created"
fi
