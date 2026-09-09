import pandas as pd
import numpy as np
from .config import DATA_PATH

# Load dataset
df = pd.read_csv(DATA_PATH)


def predict_trends():
    """
    Predicts simple trends for all numeric dataset columns.
    Uses a lightweight trend estimation suitable for hackathon demo.
    """

    predictions = {}

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:

        try:

            current_avg = float(df[col].mean())

            # Simple trend estimation (2% increase assumption)
            predicted_value = current_avg * 1.02

            trend = "increase" if predicted_value > current_avg else "decrease"

            predictions[col] = {
                "current_average": round(current_avg, 3),
                "predicted_value": round(predicted_value, 3),
                "trend": trend
            }

        except Exception:
            continue

    return predictions


def predict_metric(metric):
    """
    Returns prediction for a specific metric.
    """

    predictions = predict_trends()

    if metric in predictions:
        return predictions[metric]

    return None


def predict_ship_performance():
    """
    Returns summarized ship performance prediction.
    """

    predictions = predict_trends()

    summary = {}

    key_metrics = [
        "fuel_consumption_t_day",
        "co2_emitted_tonnes",
        "engine_load_pct",
        "avg_speed_knots",
        "wave_height_m",
        "wind_speed_knots"
    ]

    for metric in key_metrics:

        if metric in predictions:
            summary[metric] = predictions[metric]

    return summary