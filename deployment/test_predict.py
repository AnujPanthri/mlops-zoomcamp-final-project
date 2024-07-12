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

y_pred_response = requests.post(
    "http://localhost:8080/predict",
    json=dummy_data,
    timeout=10,
).json()

print(y_pred_response)
