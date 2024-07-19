from deployment.main import is_valid_json_input


def test_is_valid_json_input_valid():
    test_data = [
        {
            "Temperature[C]": 23,
            "Humidity[%]": 32,
        },
        {
            "Temperature[C]": 30,
            "Humidity[%]": 14,
        },
    ]

    assert is_valid_json_input(test_data[:1], ["Temperature[C]", "Humidity[%]"])
    assert is_valid_json_input(test_data, ["Temperature[C]", "Humidity[%]"])
    assert is_valid_json_input(test_data, ["Temperature[C]"])
    assert is_valid_json_input([test_data[0]], ["Temperature[C]", "Humidity[%]"])


def test_is_valid_json_input_invalid():
    test_data = {
        "Temperature[C]": 23,
        "Humidity[%]": 32,
    }

    assert not is_valid_json_input(test_data, ["Temperature[C]", "Humidity[%]"])
    assert not is_valid_json_input(
        [test_data], ["Temperature[C]", "Humidity[%]", "eCO2[ppm]"]
    )
