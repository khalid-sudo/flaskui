from prophet import Prophet
import mlflow
from models.prophet_model import StanInit

def train_model(prophet_model, df, date_col, value_col):
    from models.validation import identify_frequency
    frequency = identify_frequency(df, date_col)
    print(f"Identified frequency: {frequency}")

    prophet_df = df[[date_col, value_col]].rename(columns={date_col: 'ds', value_col: 'y'})
    run_id = check_existing_model(prophet_model.model_name)

    if run_id and prophet_model.warm_start:
        print("Warm starting the model using previous parameters")
        existing_model = prophet_model.load_existing_model(run_id)
        prophet_model.model = Prophet().fit(prophet_df, init=StanInit(existing_model))
    else:
        prophet_model.model = Prophet()
        prophet_model.model.fit(prophet_df)
        prophet_model.log_model(prophet_model.model, prophet_df)

    return prophet_model.model


def check_existing_model(model_name):
    client = mlflow.tracking.MlflowClient()
    try:
        runs = client.search_runs(
            experiment_ids=[client.get_experiment_by_name("Prophet_Models").experiment_id],
            filter_string=f"tags.model_name = '{model_name}'"
        )
        if runs:
            return runs[0].info.run_id
        return None
    except Exception as e:
        print(f"Error fetching model from MLflow: {str(e)}")
        return None


def load_model_from_mlflow(run_id):
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.prophet.load_model(model_uri)
    print(f"Loaded model from run ID: {run_id}")
    return model
