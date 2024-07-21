import os


def getenv(key: str, default_value: str) -> str:
    value = os.getenv(key, "")
    if value.strip() == "":
        value = None
    if value is None:
        value = default_value
    return value
