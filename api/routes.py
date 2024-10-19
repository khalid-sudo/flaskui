from flask import Blueprint, jsonify, request, render_template
from models.prophet_model import ProphetModel
from models.training import train_model, load_model_from_mlflow
from models.metrics import calculate_metrics
from models.validation import identify_frequency
from utils.file_utils import decompress_zst_file
import os
import pandas as pd

api_blueprint = Blueprint('api', __name__)

DATA_DIR = 'data'

@api_blueprint.route('/')
def home():
    return render_template('index.html')

@api_blueprint.route('/list_csv_files')
def list_csv_files():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv.zst') or f.endswith('.csv')]
    return jsonify(files)

@api_blueprint.route('/get_columns')
def get_columns():
    file = request.args.get('file')
    file_path = os.path.join(DATA_DIR, file)

    try:
        if file.endswith('.csv.zst'):
            decompressed_file = decompress_zst_file(file_path)
            if decompressed_file:
                df = pd.read_csv(decompressed_file)
            else:
                return jsonify({'error': 'Failed to decompress the file.'}), 500
        elif file.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            return jsonify({'error': 'Unsupported file format.'}), 400
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

    columns = df.columns.tolist()
    return jsonify(columns=columns)

@api_blueprint.route('/process_quality_check', methods=['POST'])
def process_quality_check():
    data = request.get_json()
    dataset = data['dataset']
    column = data.get('column')
    quality_check = data['quality_check']

    file_path = os.path.join(DATA_DIR, dataset)

    try:
        if dataset.endswith('.csv.zst'):
            decompressed_file = decompress_zst_file(file_path)
            if decompressed_file:
                df = pd.read_csv(decompressed_file)
            else:
                return jsonify({"error": "Failed to decompress file"}), 400
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        return jsonify({"error": f"Error loading file: {str(e)}"}), 400

    # If the dataset has only 'ds' and 'y', skip column selection
    if 'ds' in df.columns and 'y' in df.columns and len(df.columns) == 2:
        df['ds'] = pd.to_datetime(df['ds'])
        return handle_prophet_training(df, 'ds', 'y', dataset)
    else:
        if column:
            df['ds'] = pd.to_datetime(df['ts_recv'])
            return handle_prophet_training(df, 'ds', column, dataset)
        else:
            return jsonify({"error": "Column selection required"}), 400

@api_blueprint.route('/train_model', methods=['POST'])
def train_model_route():
    data = request.get_json()
    dataset = data['dataset']
    column = data.get('column')
    warm_start = data.get('warm_start', False)

    file_path = os.path.join(DATA_DIR, dataset)

    try:
        if dataset.endswith('.csv.zst'):
            decompressed_file = decompress_zst_file(file_path)
            if decompressed_file:
                df = pd.read_csv(decompressed_file)
            else:
                return jsonify({"error": "Failed to decompress file"}), 400
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        return jsonify({"error": f"Error loading file: {str(e)}"}), 400

    if 'ds' in df.columns and 'y' in df.columns and len(df.columns) == 2:
        df['ds'] = pd.to_datetime(df['ds'])
        return handle_prophet_training(df, 'ds', 'y', dataset, warm_start)
    else:
        if column:
            df['ds'] = pd.to_datetime(df['ds'])
            return handle_prophet_training(df, 'ds', column, dataset, warm_start)
        else:
            return jsonify({"error": "Column selection required"}), 400

def handle_prophet_training(df, date_col, value_col, model_name, warm_start=False):
    # Initialize the ProphetModel
    prophet_model = ProphetModel(model_name, warm_start)

    # Train the model
    model = prophet_model.train(df, date_col, value_col)

    # Identify frequency
    frequency = identify_frequency(df, date_col)

    # Generate forecast
    forecast = prophet_model.forecast(df, frequency)

    # Calculate metrics
    y_true = df[value_col].values
    y_pred = forecast['yhat'][:len(y_true)].values
    metrics = calculate_metrics(y_true, y_pred)

    response = {
        "forecast_plot_url": "/static/plots/forecast.png",
        "components_plot_url": "/static/plots/components.png",
        "metrics": metrics
    }

    return jsonify(response)
