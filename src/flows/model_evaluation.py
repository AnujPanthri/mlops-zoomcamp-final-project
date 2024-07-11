import boto3
from mlflow.client import MlflowClient
from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact

from src.model import Model
from src.s3_utils import download_s3_folder
from src.prepare_dataset import split_data, prepare_data, read_dataset
from constants import MODEL_DIR, MLFLOW_MODEL_NAME, MLFLOW_TRACKING_URI


@task
def read_dataset_task(numeric_cols, target, seed):
    df = read_dataset()
    X, y = prepare_data(df=df, numeric_cols=numeric_cols, target=target)
    X_train, X_val, y_train, y_val = split_data(X, y, test_size=0.2, random_state=seed)

    return X_train, X_val, y_train, y_val


@task
def download_model_from_s3_task(version: str):
    s3 = boto3.resource("s3")
    client = MlflowClient(MLFLOW_TRACKING_URI)
    mlflow_model = client.get_model_version(MLFLOW_MODEL_NAME, version=version)
    # print(mlflow_model.source)

    download_s3_folder(
        s3_resource=s3,
        s3_path=mlflow_model.source,
        local_dir=MODEL_DIR,
    )


@task
def load_model_task():
    model = Model.from_model_dir(MODEL_DIR)
    return model


@task
def calculate_accuracy_task(model, X, y):
    score = model.get_accuracy(X, y)
    return score


@flow
def evaluate_model_flow(
    mlflow_model_version: str,
    seed: int = 565,
) -> None:

    logger = get_run_logger()
    logger.info(f"evaluating model_version {mlflow_model_version}")

    download_model_from_s3_task(mlflow_model_version)

    model = load_model_task()

    X_train, X_val, y_train, y_val = read_dataset_task(
        model.numeric_cols,
        model.target,
        seed=seed,
    )

    train_acc = calculate_accuracy_task(model, X_train, y_train)
    logger.info(f"training accuracy: {train_acc:.02f}")

    val_acc = calculate_accuracy_task(model, X_val, y_val)
    logger.info(f"validation accuracy: {val_acc:.02f}")

    artifact_md = f"""# Evaluation Report
using model version: {mlflow_model_version}

- training accuracy: {train_acc}
- validation accuracy: {val_acc}
"""
    create_markdown_artifact(
        artifact_md,
        key="evaluation-report",
    )


if __name__ == "__main__":
    evaluate_model_flow(mlflow_model_version="1")
