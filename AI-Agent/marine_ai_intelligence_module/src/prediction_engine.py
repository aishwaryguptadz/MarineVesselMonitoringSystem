import numpy as np
import pandas as pd
from .voyage_analyzer import get_current_telemetry


def calculate_metric_regression(series: pd.Series):
    clean = series.dropna().tail(25)
    n = len(clean)
    if n < 4:
        return None

    y = clean.values
    t = np.arange(n)
    t_mean, y_mean = np.mean(t), np.mean(y)

    denominator = np.sum((t - t_mean) ** 2)
    slope = np.sum((t - t_mean) * (y - y_mean)) / denominator if denominator != 0 else 0.0
    intercept = y_mean - slope * t_mean

    current_val = float(y[-1])
    raw_forecast = float(slope * n + intercept)

    max_step_delta = abs(current_val) * 0.15 if current_val != 0 else 2.0
    if abs(raw_forecast - current_val) > max_step_delta:
        predicted_val = current_val + (np.sign(slope) * max_step_delta)
    else:
        predicted_val = raw_forecast

    pct_drift = ((predicted_val - current_val) / abs(current_val) * 100) if current_val != 0 else 0.0

    if pct_drift > 0.5:
        trend = "increase"
    elif pct_drift < -0.5:
        trend = "decrease"
    else:
        trend = "stable"

    return {
        "current_average": round(current_val, 2),
        "predicted_value": round(predicted_val, 2),
        "trend": trend,
        "slope": round(float(slope), 4),
        "change_pct": round(pct_drift, 1)
    }


def predict_trends(vessel_type: str = None):
    telemetry = get_current_telemetry(vessel_type)
    df = telemetry["df"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    predictions = {}
    for col in numeric_cols:
        res = calculate_metric_regression(df[col])
        if res:
            predictions[col] = res

    return predictions


def predict_metric(metric: str, vessel_type: str = None):
    telemetry = get_current_telemetry(vessel_type)
    df = telemetry["df"]

    if metric in df.columns and np.issubdtype(df[metric].dtype, np.number):
        return calculate_metric_regression(df[metric])

    return None