# pylint: disable=line-too-long

import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template

from utils import getenv
from src.model import Model
from constants import DEPLOYMENT_MODEL_DIR
from monitoring.log_evidently_metrics import (
    get_evidently_df,
    calculate_metrics,
    load_reference_df,
    save_reference_df,
    log_evidently_metrics,
)

load_dotenv()

HOST = "0.0.0.0"
PORT = 8080
temperature_col, humidity_col, eco2_col = "Temperature[C]", "Humidity[%]", "eCO2[ppm]"

model_dir = getenv("MODEL_DIR", DEPLOYMENT_MODEL_DIR)
LOG_TO_DB_FLAG = getenv("LOG_TO_DB_FLAG", "true").lower() == "true"


def is_numeric(value: int | float):
    return isinstance(value, (int, float))


def is_valid_json_input(json_data_list: list[dict], numeric_cols: list[str]) -> bool:
    if not isinstance(json_data_list, list):
        return False
    if len(json_data_list) == 0:
        return False

    for json_data in json_data_list:
        if not isinstance(json_data, dict):
            return False
        for col in numeric_cols:
            if col not in json_data:
                return False
            if not is_numeric(json_data[col]):
                return False
    return True


def create_app():

    app = Flask(__name__)

    model = Model.from_model_dir(model_dir)

    save_reference_df(model)
    reference_df = load_reference_df()

    @app.route("/", methods=["GET"])
    def home():
        context = {"numeric_cols": list(model.numeric_cols)}
        return render_template("index.html", context=context)

    @app.route("/test", methods=["GET"])
    def test():

        dummy_data = None
        response = {}

        if sorted(model.numeric_cols) == sorted(
            [temperature_col, humidity_col, eco2_col]
        ):
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
                f"http://localhost:{PORT}/predict",
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

        if not is_valid_json_input(json_request_data, model.numeric_cols):
            return jsonify(
                {"error": f"pass all the features including {model.numeric_cols}"}
            )

        data_df = pd.DataFrame(json_request_data, columns=model.numeric_cols)

        y_pred = model.predict(data_df)

        if LOG_TO_DB_FLAG:
            # log evidently metrics
            current_df = get_evidently_df(data_df, y_pred)
            metrics = calculate_metrics(reference_df, current_df, model)
            log_evidently_metrics(metrics)

        return jsonify(y_pred.tolist())

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True,
        host=HOST,
        port=PORT,
    )
