from prophet.diagnostics import cross_validation
import pandas as pd

def cross_validate_model(model, initial, period, horizon):
    df_cv = cross_validation(model, initial=initial, period=period, horizon=horizon)
    return df_cv

def identify_frequency(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col])
    time_deltas = df[date_col].diff().dropna().dt.total_seconds()
    median_delta = time_deltas.median()

    if median_delta <= 60:
        return 'S'  # Seconds
    elif median_delta <= 3600:
        return 'T'  # Minutes
    elif median_delta <= 86400:
        return 'H'  # Hours
    else:
        return 'D'  # Days



