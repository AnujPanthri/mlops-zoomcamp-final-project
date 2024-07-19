import os
import datetime
import traceback
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
DB_HOST = os.getenv("DB_HOST", "localhost")
PSYCOPG2_CONNECTION_STR = (
    f"host={DB_HOST} port=5432 " "user=monitoring password=secret dbname=monitoring"
)

# dataset column name to simplified column name
ds_col_to_simple_col = {
    'UTC': "utc",
    'Temperature[C]': "temperature",
    'Humidity[%]': "humidity",
    'TVOC[ppb]': "tvoc_ppb",
    'eCO2[ppm]': "eco2_ppm",
    'Raw H2': "raw_h2",
    'Raw Ethanol': "raw_ethanol",
    'Pressure[hPa]': "pressure_hpa",
    'PM1.0': "pm_1_0",
    'PM2.5': "pm_2_5",
    'NC0.5': "nc0_5",
    'NC1.0': "nc_1_0",
    'NC2.5': "nc_2_5",
    'CNT': "cnt",
    'Fire Alarm': "fire_alarm",
}


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
    print("saving reference df")
    reference_df.to_csv(REFERENCE_DF_PATH, index=False, header=True)


def load_reference_df() -> pd.DataFrame:
    reference_df = pd.read_csv(REFERENCE_DF_PATH)
    print("loaded reference df")
    return reference_df


def get_column_mapping(numeric_cols: List[str]) -> ColumnMapping:
    column_mapping = ColumnMapping(
        target=None,
        prediction='prediction',
        numerical_features=numeric_cols,
    )
    return column_mapping


def get_report(model: Model) -> Report:
    column_drift_metrics = []
    for col in model.numeric_cols:
        column_drift_metrics.append(
            ColumnDriftMetric(column_name=col),
        )
    report = Report(
        metrics=[
            *column_drift_metrics,
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
    report = get_report(model)
    report.run(
        reference_data=reference_df,
        current_data=current_df,
        column_mapping=column_mapping,
    )

    result = report.as_dict()

    tracked_metrics = {}
    for metric in result["metrics"]:

        col_name = (
            ds_col_to_simple_col[metric['result']['column_name']]
            if "column_name" in metric['result']
            else ""
        )

        if metric['metric'] == "ColumnDriftMetric":
            db_col_name = col_name + "__column_drift"
            tracked_metrics[db_col_name] = metric['result']['drift_score']

        elif metric['metric'] == "DatasetDriftMetric":
            db_col_name = "num_drifted_columns"
            tracked_metrics[db_col_name] = metric['result']['number_of_drifted_columns']

            db_col_name = "share_drifted_columns"
            tracked_metrics[db_col_name] = metric['result']['share_of_drifted_columns']
        else:
            raise NotImplementedError(
                (f"Unsupported evidently metric type: {metric['metric']}")
            )
    return tracked_metrics


def py_type_to_db_type(value):
    if isinstance(value, int):
        col_type = "integer"
    elif isinstance(value, float):
        col_type = "float"
    else:
        raise NotImplementedError(
            "unsupported type for " f"value: {value}, type: {type(value)}"
        )

    return col_type


def run_query(q, q_args=None):
    """run query of database"""
    try:
        with psycopg2.connect(
            PSYCOPG2_CONNECTION_STR,
        ) as conn:
            with conn.cursor() as curr:
                curr.execute(q, q_args)
                if curr.description is not None:
                    return curr.fetchall()

                return None

    except Exception as e:
        print(f"query: {q}")
        traceback.print_exc()
        raise e


def truncate_evidently_table():
    run_query("truncate TABLE evidently_metrics;")


def drop_evidently_table():
    run_query("drop TABLE if exists evidently_metrics;")


def get_evidently_table_columns():
    columns = run_query(
        """
              SELECT COLUMN_NAME from information_schema.columns
              WHERE table_name = 'evidently_metrics'

              """
    )
    columns = [value[0] for value in columns]
    return columns


def add_missing_columns_to_evidently_table(add_columns, column_values):
    assert len(add_columns) == len(column_values)
    print(f"adding missing columns: {add_columns}")
    query = """
        ALTER TABLE IF EXISTS evidently_metrics
        {add_columns}
    """
    add_columns_str = ", ".join(
        [
            (f"ADD COLUMN {add_columns[i]} " f"{py_type_to_db_type(column_values[i])}")
            for i in range(len(add_columns))
        ]
    )

    run_query(query.format(add_columns=add_columns_str))


def create_evidently_table(metrics: Dict[str, Union[int, float]]):
    create_table_statement = """
        CREATE TABLE if not exists evidently_metrics(
            timestamp timestamp,
            {columns}
        );
    """
    columns_str = ""
    for col, value in metrics.items():
        # print(col, value)
        col_type = py_type_to_db_type(value)

        columns_str += f'"{col}" {col_type},\n'

    # remove , form last column
    columns_str = columns_str[:-2]

    run_query(create_table_statement.format(columns=columns_str))


def refresh_evidently_table_schema(metrics):
    # check if columns are changed
    columns = get_evidently_table_columns()
    if len(columns) == 0:
        create_evidently_table(metrics)
    else:
        data_columns = list(metrics.keys())
        missing_columns = list(set(data_columns) - set(columns))

        if len(missing_columns) > 0:
            missing_columns_values = [metrics[col] for col in missing_columns]
            add_missing_columns_to_evidently_table(
                missing_columns,
                missing_columns_values,
            )


def log_evidently_metrics(metrics: Dict[str, Union[int, float]]):

    refresh_evidently_table_schema(metrics)

    timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))

    insert_statement = """INSERT INTO evidently_metrics
        ({columns})
        VALUES({placeholders})
    """

    columns = []
    columns.extend(list(metrics.keys()))

    query_args = []
    for col in columns:
        query_args.append(metrics[col])

    columns.append("timestamp")
    query_args.append(timestamp)

    columns_str = ", ".join([f'"{col}"' for col in columns])

    run_query(
        insert_statement.format(
            columns=columns_str, placeholders=", ".join(["%s" for _ in columns])
        ),
        query_args,
    )


if __name__ == "__main__":
    model = Model.from_model_dir(MODEL_DIR)
    save_reference_df(model)
    reference_df = load_reference_df()

    metrics = calculate_metrics(
        reference_df,
        reference_df,
        model,
    )

    drop_evidently_table()
    log_evidently_metrics(metrics)
