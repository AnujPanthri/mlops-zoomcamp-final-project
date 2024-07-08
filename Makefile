s3_bucket_name := $(shell cd infrastructure/ && tflocal output -raw model_bucket_name)

quality_checks:
	isort .
	black .
	pylint --recursive=y .

start-infrastructure:
	docker compose up localstack --build -d

create-infrastructure:
	cd infrastructure; \
	tflocal init; \
	tflocal apply -var-file="vars/local.tfvars";

# destroy-infrastructure:
# 	cd infrastructure; \
# 	tflocal destroy;

start-services:
	export S3_BUCKET_URL="s3://${s3_bucket_name}"; \
	echo "this is the s3_bucket url: $${S3_BUCKET_URL}"; \
	docker compose up db mlflow --build -d
