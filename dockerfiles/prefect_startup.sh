#!/bin/bash

set +e
prefect config set PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://prefect:secret@db:5432/prefect"
prefect work-pool create --type process local-pool
prefect server start --host 0.0.0.0 --port 4200
