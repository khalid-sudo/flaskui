import os

class Config:
    MLFLOW_TRACKING_URI = "http://localhost:5002"
    MLFLOW_S3_ENDPOINT_URL = "http://212.47.236.230:9000"
    AWS_ACCESS_KEY_ID = "admin"
    AWS_SECRET_ACCESS_KEY = "admin123"

def setup_mlflow():
    import mlflow
    mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = Config.MLFLOW_S3_ENDPOINT_URL
    os.environ["AWS_ACCESS_KEY_ID"] = Config.AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = Config.AWS_SECRET_ACCESS_KEY
