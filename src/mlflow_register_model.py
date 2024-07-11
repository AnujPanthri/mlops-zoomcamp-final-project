import mlflow
from mlflow.tracking import MlflowClient

from constants import (
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
)

client = MlflowClient(MLFLOW_TRACKING_URI)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def create_registered_model():

    client.delete_registered_model(MLFLOW_MODEL_NAME)

    registered_models = client.search_registered_models(
        filter_string=f"name='{MLFLOW_MODEL_NAME}'",
        max_results=1,
    )

    if len(registered_models) == 0:
        print(f"Creating Registered Model: {MLFLOW_MODEL_NAME}")
        client.create_registered_model(
            MLFLOW_MODEL_NAME,
            tags={
                "task": "smoke-detection",
            },
        )


def register_models_by_acc(acc_thres=70):
    print(f"registering all models with val_acc >= {acc_thres}:\n\n")

    # fetching the experiment_id
    experiment = client.search_experiments(
        filter_string=f"name='{MLFLOW_EXPERIMENT_NAME}'"
    )[0]

    # fetching all the runs in the experiment
    runs = client.search_runs(experiment.experiment_id, order_by=["metrics.val_acc ASC"])

    # Fetch the list of registered models and their versions
    registered_model_versions = client.search_model_versions(
        f"name='{MLFLOW_MODEL_NAME}'"
    )
    registered_run_ids = {version.run_id for version in registered_model_versions}

    # print(registered_run_ids)

    for run in runs:
        if run.data.metrics['val_acc'] >= acc_thres:
            model_uri = f"runs:/{run.info.run_id}/model"
            if run.info.run_id not in registered_run_ids:
                print(run.info.run_id)
                print(f"registering model from run: {run.info.run_name} ,\n {model_uri}")
                mlflow.register_model(model_uri, MLFLOW_MODEL_NAME)
            else:
                model = mlflow.search_model_versions(
                    filter_string=f"name = '{MLFLOW_MODEL_NAME}' run_id='{run.info.run_id}'"
                )[0]
                print(
                    (
                        f"Model from run: {run.info.run_name} "
                        f"is already registered as version {model.version}"
                    )
                )
            print()


if __name__ == "__main__":
    create_registered_model()
    register_models_by_acc(77)
