import os
import re
import shutil

import boto3
import mlflow
import numpy as np
import pandas as pd
from mlflow.client import MlflowClient

from src.model import Model
from src.s3_utils import download_s3_folder
from constants import (
    MODEL_DIR,
    BUCKET_NAME,
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
)

s3 = boto3.resource("s3")
client = MlflowClient(MLFLOW_TRACKING_URI)
model = client.get_model_version(MLFLOW_MODEL_NAME, version="2")
# print(model.source)

download_s3_folder(
    s3,
    model.source,
    MODEL_DIR,
)


def test_predict():
    # pylint: disable-all
    example_X_np = np.array(
        [
            [13, 45],
            [20, 20],
            [25, 40],
        ]
    )
    example_X_pd = pd.DataFrame(
        example_X_np,
        columns=["Temperature[C]", "Humidity[%]"],
    )

    # adding extra columns
    example_X_pd["extra"] = ["a", "b", "c"]

    model = Model.from_model_dir(MODEL_DIR)
    print(model.predict(example_X_np))
    print(model.predict(example_X_pd))


test_predict()
