import os
import pickle
import shutil
from typing import Dict, List, Tuple, Union, Optional
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression

from src.prepare_dataset import split_data, prepare_data, read_dataset

MODEL_DIR = Path("artifacts/model/")


class Model:
    """
    LogisticRegression sklearn wrapper for our Smoke Detector purpose
    """

    def __init__(
        self, numeric_cols: List, target: str, model: Optional[BaseEstimator] = None
    ):
        self.numeric_cols = numeric_cols
        self.target = target
        self.model = model

    @classmethod
    def from_model_dir(cls, model_dir: str):
        model_dir = Path(model_dir)
        model_bin_path = model_dir / "model.bin"
        meta_bin_path = model_dir / "meta.bin"

        if not os.path.exists(model_bin_path):
            raise FileNotFoundError(f"{model_bin_path} doesn't exists")

        if not os.path.exists(meta_bin_path):
            raise FileNotFoundError(f"{meta_bin_path} doesn't exists")

        with open(model_bin_path, "rb") as f:
            model = pickle.load(f)
            assert isinstance(model, BaseEstimator)

        with open(meta_bin_path, "rb") as f:
            meta_kwargs = pickle.load(f)

        return cls(model=model, **meta_kwargs)

    def train_model(self, X: np.ndarray, y: np.ndarray) -> BaseEstimator:
        self.model = LogisticRegression()
        self.model.fit(X=X, y=y)

    def get_accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        score = self.model.score(X, y) * 100
        return score

    def predict(self, data: Union[np.ndarray, pd.DataFrame]):
        X = None
        if isinstance(data, np.ndarray):
            X = data
        elif isinstance(data, pd.DataFrame):
            X, _ = prepare_data(data, numeric_cols=self.numeric_cols)
        else:
            raise TypeError(
                (
                    f"Unsupported datatype: {type(data)}, "
                    "passing data with either type: [np.ndarray, pd.DataFrame]"
                )
            )

        return self.model.predict(X)

    def save(self, model_dir: str):
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)

        os.makedirs(model_dir)

        # save them
        with open(model_dir / "model.bin", "wb") as f:
            f.write(pickle.dumps(self.model))

        with open(model_dir / "meta.bin", "wb") as f:
            f.write(
                pickle.dumps(
                    {
                        "numeric_cols": self.numeric_cols,
                        "target": self.target,
                    }
                )
            )


def model_training_pipeline():
    print("\nRunning model training pipeline:")

    target = "Fire Alarm"
    numeric_cols = ["Temperature[C]", "Humidity[%]"]
    seed = 565

    df = read_dataset()

    model = Model(numeric_cols=numeric_cols, target=target)

    X, y = prepare_data(df=df, numeric_cols=model.numeric_cols, target=model.target)
    X_train, X_val, y_train, y_val = split_data(X, y, test_size=0.2, random_state=seed)

    print("Training data shape(X,y):", X_train.shape, y_train.shape)
    print("Validation data shape(X,y):", X_val.shape, y_val.shape)

    model.train_model(X_train, y_train)

    score = model.get_accuracy(X_train, y_train)
    print(f"Training Accuracy: {score:.4f}")

    score = model.get_accuracy(X_val, y_val)
    print(f"Validation Accuracy: {score:.4f}")

    print("Saving model artifacts")
    model.save(MODEL_DIR)
    print(f"Model artifacts saved to {MODEL_DIR}")


def evaluate_model_pipeline():
    print("\nRunning evaluate model pipeline:")
    seed = 565

    df = read_dataset()

    model = Model.from_model_dir(MODEL_DIR)

    X, y = prepare_data(df=df, numeric_cols=model.numeric_cols, target=model.target)
    X_train, X_val, y_train, y_val = split_data(X, y, test_size=0.2, random_state=seed)

    score = model.get_accuracy(X_train, y_train)
    print(f"Training Accuracy: {score:.4f}")

    score = model.get_accuracy(X_val, y_val)
    print(f"Validation Accuracy: {score:.4f}")


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


if __name__ == "__main__":
    model_training_pipeline()
    evaluate_model_pipeline()
    # test_predict()
