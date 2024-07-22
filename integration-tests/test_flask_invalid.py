# pylint: disable=duplicate-code
import requests


def test_fn(json_payload, expected_response, response_type=list):
    actual_response = requests.post(
        "http://localhost:8080/predict",
        json=json_payload,
        timeout=10,
    ).json()

    print("actual_response:", actual_response)
    print("expected_response:", expected_response)

    assert isinstance(actual_response, response_type)
    assert actual_response == expected_response


# Case 1
dummy_data = [
    {
        "Humidity[%]": 30,
        "Temperature[C]": 20,
    },
    {
        "Temperature[C]": 40,
        "Humidity[%]": 100,
        "eCO2[ppm]": 60,
    },
]

numeric_cols = ["Humidity[%]", "Temperature[C]", "eCO2[ppm]"]
expected_response = {"error": f"pass all the features including {numeric_cols}"}
test_fn(dummy_data, expected_response, dict)

# Case 2
dummy_data = []
expected_response = {"error": "include at least one example"}
test_fn(dummy_data, expected_response, dict)

# Case 3
expected_response = {"error": "pass json only"}
test_fn(None, expected_response, dict)
