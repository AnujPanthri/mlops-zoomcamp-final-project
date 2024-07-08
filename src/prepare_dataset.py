import os
import shutil
from typing import Tuple, Optional
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from constants import ZIP_PATH, FILE_PATH, EXTRACTED_DIR


def unzip_dataset():
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(
            (
                f"{ZIP_PATH} missing. "
                "Download it from "
                "kaggle link: "
                "https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset"
            )
        )

    if os.path.exists(EXTRACTED_DIR):
        shutil.rmtree(EXTRACTED_DIR)

    os.makedirs(EXTRACTED_DIR)

    with ZipFile(ZIP_PATH, "r") as zip_file:
        zip_file.extractall(EXTRACTED_DIR)
    assert os.path.exists(FILE_PATH)


def read_dataset():
    if not os.path.exists(FILE_PATH):
        unzip_dataset()
    df = pd.read_csv(FILE_PATH)
    return df


def prepare_data(
    df: pd.DataFrame, numeric_cols: list, target: Optional[str] = None
) -> Tuple[
    np.ndarray,
    np.ndarray,
]:
    X = df[numeric_cols].values
    y = None
    if target is not None:
        y = df[target].values

    return X, y


def split_data(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float,
    random_state=None,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
    )
    return X_train, X_val, y_train, y_val
