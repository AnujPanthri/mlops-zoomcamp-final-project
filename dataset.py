from zipfile import ZipFile
import os
from pathlib import Path
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split

ZIP_PATH = Path("dataset/smoke_detection_iot.csv.zip")
EXTRACTED_DIR = Path("dataset/extracted/")
FILE_PATH = EXTRACTED_DIR / "smoke_detection_iot.csv"

def unzip_dataset():
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError((
            f"{ZIP_PATH} missing. "
            "Download it from "
            "kaggle link: https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset"
            ))

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

# def split_dataset(df:pd.DataFrame, random_state=None, ):
#     train_test_split(df, )