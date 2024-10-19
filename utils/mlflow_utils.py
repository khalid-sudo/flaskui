from mlflow.tracking import MlflowClient
import mlflow

def check_existing_model(model_name):
    client = MlflowClient()
    experiment = client.get_experiment_by_name("Prophet_Models")
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], filter_string=f"tags.model_name = '{model_name}'")
    if runs:
        return runs[0].info.run_id
    return None

def log_model(model, model_name):
    with mlflow.start_run() as run:
        mlflow.prophet.log_model(model, artifact_path="model")
        mlflow.set_tag("model_name", model_name)
