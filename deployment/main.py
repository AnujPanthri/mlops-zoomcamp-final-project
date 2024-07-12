import os

import boto3
import requests
import numpy as np
from mlflow.client import MlflowClient
from flask import Flask, Response, jsonify, request

from src.model import Model
from src.s3_utils import download_s3_folder
from constants import MODEL_DIR, MLFLOW_MODEL_NAME, MLFLOW_TRACKING_URI

mlflow_model_version = os.getenv("MLFLOW_MODEL_VERSION", "2")
client = MlflowClient(MLFLOW_TRACKING_URI)
mlflow_model = client.get_model_version(MLFLOW_MODEL_NAME, mlflow_model_version)
s3_resource = boto3.resource("s3")

host = "0.0.0.0"
port = 8080

app = Flask(__name__)

temperature_col, humidity_col, eco2_col = "Temperature[C]", "Humidity[%]", "eCO2[ppm]"

download_s3_folder(
    s3_resource,
    s3_path=mlflow_model.source,
    local_dir=MODEL_DIR,
)

model = Model.from_model_dir(MODEL_DIR)


@app.route("/", methods=["GET"])
def home():
    html = """
    <a href="/test">test link<a>
"""
    return Response(html, mimetype="text/html")


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
        dummy_data = {
            "Temperature[C]": 40,
            "Humidity[%]": 100,
            "eC02[ppm]": 60,
        }

    if dummy_data is None:
        response = {
            "numeric_cols": model.numeric_cols,
            "msg": "we don't have dummy data for this model",
        }

    else:
        y_pred_response = requests.post(
            f"http://{host}:{port}/predict",
            data=dummy_data,
            timeout=10,
        ).json()

        response = {
            "numeric_cols": model.numeric_cols,
            "data": dummy_data,
            "response": y_pred_response,
        }

    return jsonify(response)


@app.route("/predict", method=["POST"])
def predict():
    # pylint: disable=broad-exception-raised

    temperature = request.form.get("Temperature[C]")
    humidity = request.form.get("Humidity[%]")
    eco2 = request.form.get("eC02[ppm]")

    field_missing_msg = "{} field is missing"

    if temperature is None and temperature_col in model.numeric_cols:
        return jsonify({"error": field_missing_msg.format(temperature_col)})

    if humidity is None and humidity_col in model.numeric_cols:
        return jsonify({"error": field_missing_msg.format(humidity_col)})

    if eco2 is None and eco2_col in model.numeric_cols:
        return jsonify({"error": field_missing_msg.format(eco2_col)})

    # now run the model
    data = []

    for col in model.numeric_cols:
        if col == temperature_col:
            data.append(temperature)
        elif col == humidity_col:
            data.append(humidity_col)
        elif col == eco2_col:
            data.append(eco2)
        else:
            raise Exception(f"unknown column: {col} required by model")

    data = np.array([data])
    y_pred = model.predict(data)
    y_pred = y_pred.tolist()

    return jsonify(y_pred)


if __name__ == "__main__":
    app.run(
        debug=True,
        host=host,
        port=port,
    )
