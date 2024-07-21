import os
from pathlib import Path

ZIP_PATH = Path("dataset/smoke_detection_iot.csv.zip")
EXTRACTED_DIR = Path("dataset/extracted/")
FILE_PATH = EXTRACTED_DIR / "smoke_detection_iot.csv"
ARTIFACT_DIR = Path("artifacts/")
MODEL_DIR = ARTIFACT_DIR / "model/"
MONITORING_ARTIFACT_DIR = ARTIFACT_DIR / "monitoring/"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = "smoke-detection"
MLFLOW_MODEL_NAME = "smoke-detection-model"
BUCKET_NAME = "smoke-detector-model-bucket"
SEED = 565
TEST_SIZE = 0.2
DEPLOYMENT_MODEL_DIR = ARTIFACT_DIR / "deployment/model/"
