# Smoke Detector
[![Unit tests](https://github.com/AnujPanthri/mlops-zoomcamp-final-project/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/AnujPanthri/mlops-zoomcamp-final-project/actions/workflows/unit_tests.yml)
[![Integration Tests](https://github.com/AnujPanthri/mlops-zoomcamp-final-project/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/AnujPanthri/mlops-zoomcamp-final-project/actions/workflows/integration_tests.yml)

This is an project for final project submission of the DataTalksClub MLOps ZoomCamp 2024.

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
- [X] model deployment
- [X] model monitoring
- [X] write unit tests
- [X] write integration tests
- [X] add github action to run unit tests
- [X] add github action to run integration tests


## Note :-
- It is recommended for windows users to run every command specified below in git bash.
- Always run ```pipenv shell``` to activate the pipenv environment in a new terminal before running any of the below commands

## Setup Dependencies :-
- install **python 3.11.4** if not installed or install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#automatic-installer)
- install **docker** if not installed
- install **terraform** if not installed
- install **make** if not installed

```bash
make install
```

## Setup for Contribution :-
```bash
make install
pre-commit install
```

## Setup for infrastructure :-
I am using tflocal which is an wrapper for terraform which allows us to run terraform locally with localstack.

**Note:-** the localstack official docker image provides persistence only in pro version so instead of using it I am using this different localstack image which supports presistence for free.
https://hub.docker.com/r/gresau/localstack-persist

This command is used to start an localstack container and initialize an s3 bucket as specified in terraform.
```bash
make create-infra
```

## Start Services :-
Note:- this command also runs the ```make create-infra``` command internally so use can directly run this.
```bash
make start-services
```

it starts postgresql, mlflow, prefect and evidently services.

- postgresql: http://localhost:5432/
- mlflow: http://localhost:5000/
- prefect: http://localhost:4200/
- evidently: http://localhost:3000/

## Train model :-
### Workflow Orchestration :-
I have used ```prefect``` instead of ```Mage``` as it seems more reliable to me.

In prefect we use ```task``` and ```flow``` in place of ```block``` and ```pipeline``` in mage. And we need to deploy ```flow``` so that we can run them on a schedule.

### Register deployments :-
```bash
prefect deploy --all
```

### Add a worker to prefect work pool local-pool :-
we have made up an local process work pool which we are gonna use to run our deployments on, but before we run a deployment we will need to start an worker for our work pool ```local-pool``` on a new terminal (always run pipenv shell before anything).

```bash
make local-work-pool-worker
```

### Run deployments from prefect ui :-

open http://localhost:4200/deployments and run deployments.
Also you can see the progress of the run on prefect dashboard.

the list of deployed flows :-
- ```simple_model_training```: it is used to train a single model with the given numeric_cols.

- ```simple-model-feature-selection-search```: it is used to train multiple models using different set of features to compare which set of features gives us the best models, all the experiments are tracked and logged with mlflow so you can check their correponding runs on mlflow.

- ```model-evaluation```: it is used to evaluate an model registered by mlflow, **so before running this you need to register the models using ```src/mlflow_register_model.py``` script**.

### Register best models in mlflow :-
This script is used to register all the best model which have an validation accuracy more than 77%. Also it doesn't registers the same run model twice even if you run this script twice.
```bash
python -m src.mlflow_register_model
```

## Model Deployment :-
I am using flask to serve the model, which is downloaded from the model registry of mlflow. Model version is configurable via ```MLFLOW_MODEL_VERSION``` environment variable.

you can set the model version before running the deployment scripts, example :-
```bash
export MLFLOW_MODEL_VERSION="1"
```

### To run deployment in current environment :-
```bash
make dev-deploy
```

### To run deployment in a docker container :-
**Note:-** this expects the Pipfile.lock file to be present in the root dir of the project so either run ```pipenv lock``` to generate it or run ```make install``` to install the dependencies and also generate the Pipfile.lock file.
```bash
make deploy
```

you can access the deployment website on http://localhost:8080/ in both the cases.

### Use deployed model :-
Open the url http://localhost:8080/ and there you can play with the model.
or
access it by doing an POST request to the endpoint http://localhost:8080/predict/ which expects json data as list of features of each example we want prediction for and returns an list of values either 0 or 1 where 1 means smoke is detected and 0 means no smoke is detected.

#### Example:

POST request to:
```
http://localhost:8080/predict/
```
with json payload :-
```json
[
    {
        "Humidity[%]": 30,
        "Temperature[C]": 20,
        "eCO2[ppm]": 12
    },
    {
        "Temperature[C]": 40,
        "Humidity[%]": 100,
        "eCO2[ppm]": 60
    },
]
```

Json response :-
```json
[0, 1]
```

## Testing:-

### To Run Unit Tests:-
```bash
make test
```

### To run Integration Tests:-
**Note:-** this expects the Pipfile.lock file to be present in the root dir of the project so either run ```pipenv lock``` to generate it or run ```make install``` to install the dependencies and also generate the Pipfile.lock file.
```bash
make integration-test
```


## Remove Containers :-
### Remove all Containers :-
```bash
docker compose down
```

### Remove selected Containers :-
```bash
docker compose down {services names space seperated}
```

example to remove localstack and postgres containers:-
```bash
docker compose down localstack db
```

## Docker Hub

I have also push one container to docker hub you can [check it out](https://hub.docker.com/r/anujpanthri/smoke-detector).

### To run in interactive mode:-
```bash
docker run --name smoke-detector -p 8080:8080 -e LOG_TO_DB_FLAG=false --rm -it anujpanthri/smoke-detector
```
### To run in detached mode:-
```bash
docker run --name smoke-detector -p 8080:8080 -e LOG_TO_DB_FLAG=false -d anujpanthri/smoke-detector
```
### To remove container:-
```bash
docker stop smoke-detector
docker rm smoke-detector
```
### To remove container forcefully:-
```bash
docker rm smoke-detector --force
```

## Screenshots
![Screenshot 2024-07-21 212151](https://github.com/user-attachments/assets/3f88b011-ef21-45ba-a5e1-553561471431)
![image](https://github.com/user-attachments/assets/eeedb12b-a48a-42e2-ae58-913e814656fe)
![image](https://github.com/user-attachments/assets/18915ae6-4444-4c3d-8895-717214281981)

