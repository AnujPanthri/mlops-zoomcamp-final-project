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
- [ ] using mlflow to track the training experiments and for Model Registry
- [ ] using workflow orchestrator(Prefect) to manage the training pipeline
- [ ] model deployment
- [ ] model monitoring
- [ ] writing unit tests and integration tests


## Setup for Contribution

```bash
pipenv install
pipenv shell
pre-commit install
```

## Setup for infrastructure

I am using tflocal which is an wrapper for terraform which allows us to run terraform locally with localstack.

```bash
tflocal init
tflocal plan
tflocal apply
```
