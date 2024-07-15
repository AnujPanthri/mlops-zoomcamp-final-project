# pylint: disable=line-too-long

import os

import boto3
import requests
import numpy as np
import pandas as pd
from mlflow.client import MlflowClient
from flask import Flask, jsonify, request, render_template

from src.model import Model
from src.s3_utils import download_s3_folder
from constants import MODEL_DIR, MLFLOW_MODEL_NAME, MLFLOW_TRACKING_URI
from monitoring.log_evidently_metrics import (
    get_evidently_df,
    calculate_metrics,
    load_reference_df,
    save_reference_df,
    log_evidently_metrics,
    truncate_evidently_table,
)


def download_mlflow_model():
    mlflow_model_version = os.getenv("MLFLOW_MODEL_VERSION", "2")
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", MLFLOW_TRACKING_URI)
    # print(mlflow_tracking_uri)
    # print(MLFLOW_MODEL_NAME, mlflow_model_version)
    client = MlflowClient(mlflow_tracking_uri)
    mlflow_model = client.get_model_version(MLFLOW_MODEL_NAME, mlflow_model_version)
    s3_resource = boto3.resource("s3")

    download_s3_folder(
        s3_resource,
        s3_path=mlflow_model.source,
        local_dir=MODEL_DIR,
    )


def is_valid_json_input(json_data_list: list[dict]) -> bool:
    for data_json in json_data_list:
        if not set(model.numeric_cols).issubset(set(data_json.keys())):
            return False
    return True


################################################ Initializing some globals ###########################################################
host = "0.0.0.0"
port = 8080

app = Flask(__name__)

download_mlflow_model()
model = Model.from_model_dir(MODEL_DIR)

temperature_col, humidity_col, eco2_col = "Temperature[C]", "Humidity[%]", "eCO2[ppm]"

############################################## evidently metrics related #############################################################
save_reference_df(model)
reference_df = load_reference_df()
truncate_evidently_table()


@app.route("/", methods=["GET"])
def home():
    context = {"numeric_cols": list(model.numeric_cols)}
    return render_template("index.html", context=context)


@app.route("/test", methods=["GET"])
def test():

    dummy_data = None
    response = {}

    if sorted(model.numeric_cols) == sorted([temperature_col, humidity_col, eco2_col]):
        dummy_data = np.array(
            [
                [20, 30, 12],
                [40, 100, 60],
            ]
        )
        dummy_data = [
            {
                "Humidity[%]": 30,
                "Temperature[C]": 20,
                "eCO2[ppm]": 12,
            },
            {
                "Temperature[C]": 40,
                "Humidity[%]": 100,
                "eCO2[ppm]": 60,
            },
        ]

    if dummy_data is None:
        response = {
            "numeric_cols": model.numeric_cols,
            "msg": "we don't have dummy data for this model",
        }

    else:
        y_pred_response = requests.post(
            f"http://localhost:{port}/predict",
            json=dummy_data,
            timeout=10,
        ).json()

        response = {
            "numeric_cols": model.numeric_cols,
            "data": dummy_data,
            "response": y_pred_response,
        }

    return jsonify(response)


@app.route("/predict", methods=["POST"])
def predict():
    # pylint: disable=broad-exception-raised
    if request.is_json:
        json_request_data = request.get_json()
    else:
        return jsonify({"error": "pass json only"})

    if not isinstance(json_request_data, list):
        return jsonify({"error": "pass list of features"})

    if not is_valid_json_input(json_request_data):
        return jsonify({"error": f"pass all the features including {model.numeric_cols}"})

    data_df = pd.DataFrame(json_request_data, columns=model.numeric_cols)

    y_pred = model.predict(data_df)

    # log evidently metrics
    current_df = get_evidently_df(data_df, y_pred)
    metrics = calculate_metrics(reference_df, current_df, model)
    log_evidently_metrics(metrics)

    return jsonify(y_pred.tolist())


if __name__ == "__main__":
    app.run(
        debug=True,
        host=host,
        port=port,
    )
