s3_bucket_name := $(shell cd infrastructure/ && tflocal output -raw model_bucket_name)
install:
	pip install pipenv
	pipenv install --dev
	pipenv run prefect config set PREFECT_API_URL="http://localhost:4200/api"
	mkdir -p persistence/localstack_data/
	mkdir -p persistence/postgresql_data/

quality-checks:
	isort .
	black .
	pylint --recursive=y .

start-infra:
	docker compose up localstack --build -d

create-infra: start-infra

	@if [ "$(auto-approve)" = "yes" ]; then \
		auto_approve_statement="-auto-approve"; \
	else \
		auto_approve_statement=""; \
	fi; \
	cd infrastructure; \
	tflocal init; \
	tflocal apply -var-file="vars/local.tfvars" $${auto_approve_statement};

# destroy-infra:
# 	cd infrastructure; \
# 	tflocal destroy;

start-services: create-infra
	export S3_BUCKET_URL="s3://${s3_bucket_name}"; \
	echo "this is the s3_bucket url: $${S3_BUCKET_URL}"; \
	docker compose up db mlflow prefect grafana --build -d

dev-deploy:
	export AWS_REGION=us-east-1; \
	export AWS_ENDPOINT_URL=http://localhost:4566; \
	export AWS_ACCESS_KEY_ID=access_key_id; \
	export AWS_SECRET_ACCESS_KEY=secret_access_key; \
	export MODEL_DIR=artifacts/deployment/model/; \
	python -m deployment.download_model; \
	python -m deployment.main

deploy:
	docker compose up deployment --build -d

clear-persistence:
	rm -r ./persistence/localstack_data/*
	rm -r ./persistence/postgresql_data/*

local-work-pool:
	prefect work-pool create --type process local-pool

local-work-pool-worker:
	export AWS_REGION=us-east-1; \
	export AWS_ENDPOINT_URL=http://localhost:4566; \
	export AWS_ACCESS_KEY_ID=access_key_id; \
	export AWS_SECRET_ACCESS_KEY=secret_access_key; \
	prefect worker start --pool local-pool;

test:
	pytest tests/

integration-test:
	./integration-tests/run.sh
