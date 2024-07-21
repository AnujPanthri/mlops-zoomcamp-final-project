import boto3
from mlflow.client import MlflowClient

from utils import getenv
from src.s3_utils import download_s3_folder
from constants import (
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    DEPLOYMENT_MODEL_DIR,
)

model_dir = getenv("MODEL_DIR", DEPLOYMENT_MODEL_DIR)

model_dir = getenv("MODEL_DIR", DEPLOYMENT_MODEL_DIR)
DOWLOAD_MODEL_FLAG = getenv("DOWLOAD_MODEL_FLAG", "true").lower() == "true"


def download_mlflow_model():

    mlflow_model_version = getenv("MLFLOW_MODEL_VERSION", "2")
    mlflow_tracking_uri = getenv("MLFLOW_TRACKING_URI", MLFLOW_TRACKING_URI)

    print(f"Downloading mlflow_model_version: {mlflow_model_version}")
    # print(mlflow_tracking_uri)
    # print(MLFLOW_MODEL_NAME, mlflow_model_version)
    client = MlflowClient(mlflow_tracking_uri)
    mlflow_model = client.get_model_version(MLFLOW_MODEL_NAME, mlflow_model_version)
    s3_resource = boto3.resource("s3")

    download_s3_folder(
        s3_resource,
        s3_path=mlflow_model.source,
        local_dir=model_dir,
    )


if __name__ == "__main__":
    if DOWLOAD_MODEL_FLAG:
        download_mlflow_model()
    else:
        print(
            (
                "Skipping model download from mlflow, "
                "set DOWLOAD_MODEL_FLAG=True "
                "enviroment variable to download model."
            )
        )
