s3_bucket_name := $(shell cd infrastructure/ && tflocal output -raw model_bucket_name)

install:
	pip install pipenv
	pipenv install
	prefect config set PREFECT_API_URL="http://localhost:4200/api"

quality-checks:
	isort .
	black .
	pylint --recursive=y .

start-infra:
	docker compose up localstack --build -d

create-infra:
	cd infrastructure; \
	tflocal init; \
	tflocal apply -var-file="vars/local.tfvars";

# destroy-infra:
# 	cd infrastructure; \
# 	tflocal destroy;

start-services:
	export S3_BUCKET_URL="s3://${s3_bucket_name}"; \
	echo "this is the s3_bucket url: $${S3_BUCKET_URL}"; \
	docker compose up db mlflow prefect --build -d


local-work-pool:
	prefect work-pool create --type process local-pool

local-work-pool-worker:
	prefect worker start --pool local-pool
