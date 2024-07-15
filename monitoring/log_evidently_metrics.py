import os
import datetime
from typing import Dict, List, Union

import pytz
import psycopg2
import numpy as np
import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric

from src.model import Model
from src.prepare_dataset import split_data, prepare_data, read_dataset
from constants import SEED, MODEL_DIR, TEST_SIZE, MONITORING_ARTIFACT_DIR

os.makedirs(MONITORING_ARTIFACT_DIR, exist_ok=True)

REFERENCE_DF_PATH = MONITORING_ARTIFACT_DIR / "reference.csv"


def _get_reference_data(
    numeric_cols: List[str],
    target: str,
) -> np.ndarray:
    df = read_dataset()
    X, y = prepare_data(df, numeric_cols=numeric_cols, target=target)
    X_train, _, _, _ = split_data(X, y, test_size=TEST_SIZE, random_state=SEED)
    return X_train


def calculate_evidently_df(
    model: Model,
    X: np.ndarray,
) -> pd.DataFrame:
    df = pd.DataFrame(X, columns=model.numeric_cols)
    df['prediction'] = model.predict(df)
    return df


def get_evidently_df(
    df: pd.DataFrame,
    y_pred: np.ndarray,
) -> pd.DataFrame:
    df['prediction'] = y_pred
    return df


def _calc_reference_df(model: Model) -> pd.DataFrame:
    X = _get_reference_data(model.numeric_cols, model.target)
    reference_df = calculate_evidently_df(model, X)
    return reference_df


def save_reference_df(model: Model) -> None:
    reference_df = _calc_reference_df(model)
    reference_df.to_csv(REFERENCE_DF_PATH, index=False, header=True)


def load_reference_df() -> pd.DataFrame:
    reference_df = pd.read_csv(REFERENCE_DF_PATH)
    return reference_df


def get_column_mapping(numeric_cols: List[str]) -> ColumnMapping:
    column_mapping = ColumnMapping(
        target=None,
        prediction='prediction',
        numerical_features=numeric_cols,
    )
    return column_mapping


def get_report() -> Report:
    report = Report(
        metrics=[
            ColumnDriftMetric(column_name="Temperature[C]"),
            ColumnDriftMetric(column_name="Humidity[%]"),
            ColumnDriftMetric(column_name="eCO2[ppm]"),
            DatasetDriftMetric(),
        ]
    )
    return report


def calculate_metrics(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    model: Model,
) -> dict:

    column_mapping = get_column_mapping(model.numeric_cols)
    report = get_report()
    report.run(
        reference_data=reference_df,
        current_data=current_df,
        column_mapping=column_mapping,
    )

    result = report.as_dict()

    metrics = {
        "temperature_drift": result["metrics"][0]['result']['drift_score'],
        "humidity_drift": result["metrics"][1]['result']['drift_score'],
        "eCO2_drift": result["metrics"][2]['result']['drift_score'],
        "num_drifted_columns": result["metrics"][3]['result'][
            'number_of_drifted_columns'
        ],
    }

    return metrics


def truncate_evidently_table():
    truncate_statement = """
        truncate TABLE evidently_metrics;
    """
    with psycopg2.connect(
        "host=localhost port=5432 user=monitoring password=secret dbname=monitoring",
    ) as conn:
        with conn.cursor() as curr:
            curr.execute(truncate_statement)


def create_evidently_table():
    create_table_statement = """
        CREATE TABLE if not exists evidently_metrics(
            timestamp timestamp,
            temperature_drift float,
            humidity_drift float,
            eCO2_drift float,
            num_drifted_columns integer
        );
    """

    with psycopg2.connect(
        "host=localhost port=5432 user=monitoring password=secret dbname=monitoring",
    ) as conn:
        with conn.cursor() as curr:
            curr.execute(create_table_statement)


def log_evidently_metrics(metrics: Dict[str, Union[int, float]]):

    timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))

    with psycopg2.connect(
        "host=localhost port=5432 user=monitoring password=secret dbname=monitoring",
    ) as conn:
        with conn.cursor() as curr:
            curr.execute(
                (
                    "INSERT INTO evidently_metrics"
                    "(timestamp, temperature_drift, humidity_drift, "
                    "eCO2_drift, num_drifted_columns)"
                    "VALUES(%s, %s, %s, %s, %s)"
                ),
                (
                    timestamp,
                    metrics['temperature_drift'],
                    metrics['humidity_drift'],
                    metrics['eCO2_drift'],
                    metrics['num_drifted_columns'],
                ),
            )


create_evidently_table()

if __name__ == "__main__":
    model = Model.from_model_dir(MODEL_DIR)
    save_reference_df(model)
    reference_df = load_reference_df()
    metrics = calculate_metrics(
        reference_df,
        reference_df,
        model,
    )

    log_evidently_metrics(metrics)
