import numpy as np
import pandas as pd
from prophet import Prophet
from mlflow.tracking import MlflowClient
import mlflow
import os


class ProphetModel:
    def __init__(self, model_name, warm_start=False):
        self.model_name = model_name
        self.client = MlflowClient()
        self.model = None
        self.warm_start = warm_start

    def train(self, df, date_col, value_col):
        from models.training import train_model
        return train_model(self, df, date_col, value_col)

    def forecast(self, prophet_df, frequency):
        future = self.model.make_future_dataframe(periods=30, freq=frequency)
        return self.model.predict(future)

    def log_model(self, model, df):
        with mlflow.start_run() as run:
            mlflow.prophet.log_model(model, artifact_path="model")
            mlflow.set_tag("model_name", self.model_name)
            print(f"Model '{self.model_name}' trained and logged to MLflow.")

    def load_existing_model(self, run_id):
        model_uri = f"runs:/{run_id}/model"
        self.model = mlflow.prophet.load_model(model_uri)
        print(f"Loaded model from run ID: {run_id}")
        return self.model


class StanInit:
    def __init__(self, model):
        self.params = {
            'k': np.mean(model.params['k']),
            'm': np.mean(model.params['m']),
            'sigma_obs': np.mean(model.params['sigma_obs']),
            'delta': np.mean(model.params['delta'], axis=0),
            'beta': np.mean(model.params['beta'], axis=0)
        }

    def __call__(self):
        return self.params
