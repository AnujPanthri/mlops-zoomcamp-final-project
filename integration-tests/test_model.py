# pylint: disable=duplicate-code
import requests

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

expected_response = [0, 1]
actual_response = requests.post(
    "http://localhost:8080/predict",
    json=dummy_data,
    timeout=10,
).json()

print(actual_response)

assert isinstance(actual_response, list)
assert actual_response == expected_response
