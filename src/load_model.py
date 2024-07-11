import os
import re
import shutil

import boto3
import mlflow
import numpy as np
import pandas as pd
from mlflow.client import MlflowClient

from src.model import Model
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


def s3_path_to_bucket_folder(s3_path):
    match = re.search(
        r"s3://([^/]+)/",
        s3_path,
    )
    # print(match.end())
    bucket_name, s3_folder = s3_path[5 : match.end() - 1], s3_path[match.end() :]
    # print(bucket_name, s3_folder)
    return bucket_name, s3_folder


def download_s3_folder(s3_path, local_dir):
    bucket_name, s3_folder = s3_path_to_bucket_folder(s3_path)
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        print(target)
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)


download_s3_folder(
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
