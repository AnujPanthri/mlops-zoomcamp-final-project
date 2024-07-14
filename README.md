# Smoke Detector
this is an project for final project submission of the DataTalksClub MLOps ZoomCamp 2024.

## The Problem Statement

So given the informations from the different sensors found in an smoke detector can we come up with an machine learning model which can monitor the sensor's data and predict when the smoke alarm should detect smoke.

## Parts

- [X] initial experiment notebook
- [X] setup environment(using pipenv)
- [X] making scripts for training
- [X] setup pre-commit hooks
- [X] add Makefile
- [X] using terraform for provisioning the cloud infrastructure(s3 bucket) involved in this project
- [X] add persistence for localstack and postgresql containers
- [X] using mlflow to track the training experiments and for Model Registry
- [X] using workflow orchestrator(Prefect) to manage the training pipeline
- [ ] model deployment
- [ ] model monitoring
- [ ] writing unit tests and integration tests

## Setup Dependencies
install **python 3.11** if not installed
also install **docker** if not installed
also install **terraform** if not installed
also install **make** if not installed

```bash
make install
```

## Setup for Contribution

```bash
make install
pre-commit install
```

## Setup for infrastructure

I am using tflocal which is an wrapper for terraform which allows us to run terraform locally with localstack.

```bash
make start-infra
make create-infra
```


## Start other services

```bash
make start-services
```

it starts postgresql, mlflow, and prefect.

- postgresql: http://localhost:5432/
- mlflow: http://localhost:5000/
- prefect: http://localhost:4200/

## Train model

### register deployments:
```bash
prefect deploy --all
```

### add a worker to prefect work pool local-pool:
we have made up an local process work pool which we are gonna use to run our deployments on, but before we run a deployment we will need to start an worker for our work pool ```local-pool``` on a new terminal(always run pipenv shell before anything).

```bash
make local-work-pool-worker
```

### run deployments from prefect ui :-

open http://localhost:4200/deployments and run deployments.

- ```simple_model_training```: it is used to train a single model with the given numeric_cols.

- ```simple-model-feature-selection-search```: it is used to train multiple models using different set of features to compare which set of features gives us the best models, all the experiments are tracked and logged with mlflow so you can check their correponding runs on mlflow.

- ```model-evaluation```: it is used to evaluate an model registered by mlflow, **so before running this you need to register the models using ```src/mlflow_register_model.py``` script**.

### register best models:
```bash
python -m src.mlflow_register_model
```

## Model Deployment
I am using flask to serve the model, which is read from the model registry of mlflow. Model version is configurable via ```MLFLOW_MODEL_VERSION``` environment variable.

```bash
python -m deployment.main
```

### test deployed model
```bash
python -m deployment.test_predict
```


## USE THIS instead of localstack
https://hub.docker.com/r/gresau/localstack-persist
