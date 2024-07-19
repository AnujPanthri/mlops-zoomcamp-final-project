import pytest
import numpy as np
import pandas as pd

from src.model import Model


def get_numeric_cols():
    return ["Temperature[C]", "Humidity[%]"]


def get_target():
    return "Fire Alarm"


def get_model_object(model=None):
    model = Model(numeric_cols=get_numeric_cols(), target=get_target(), model=model)
    return model


def test_model_instantiation():
    model = get_model_object()
    assert model.numeric_cols == sorted(get_numeric_cols())
    assert model.target == get_target()
    assert model.model is None


class ModelMock:
    """Mock Model"""

    # pylint: disable=all

    def predict(self, X):
        return X.shape


def test_model_instantiation_with_model():
    model = get_model_object(model=ModelMock())
    assert model.model is not None
    assert isinstance(model.model, ModelMock)


def get_dummy_data(return_df=False):
    dummy_data = np.array(
        [
            [12, 45],
            [34, 412],
            [45, 78],
        ]
    )

    if return_df:
        dummy_data = pd.DataFrame(dummy_data, columns=get_numeric_cols())

    return dummy_data


def test_predict_np():
    model = get_model_object(model=ModelMock())
    dummy_np_data = get_dummy_data()

    y_actual = model.predict(dummy_np_data)
    y_expected = (3, 2)

    assert y_actual == y_expected


def test_predict_df():
    model = get_model_object(model=ModelMock())
    dummy_df_data = get_dummy_data(return_df=True)

    y_actual = model.predict(dummy_df_data)
    y_expected = (3, 2)

    assert y_actual == y_expected


def test_predict_other():
    model = get_model_object(model=ModelMock())
    dummy_other_data = get_dummy_data(return_df=True)
    dummy_other_data = dummy_other_data.to_dict(orient="records")

    with pytest.raises(TypeError) as excinfo:
        model.predict(dummy_other_data)

    assert excinfo.type is TypeError
