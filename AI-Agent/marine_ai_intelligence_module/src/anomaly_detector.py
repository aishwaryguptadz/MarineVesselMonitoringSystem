import pandas as pd
from .config import DATA_PATH


def detect_anomalies():

    try:
        df = pd.read_csv(DATA_PATH)

        anomalies = []

        # Engine load anomaly
        if "engine_load_pct" in df.columns:
            if df["engine_load_pct"].mean() > 80:
                anomalies.append("Critical engine overload detected")

        # Extreme sea state
        if "wave_height_m" in df.columns:
            if df["wave_height_m"].mean() > 4:
                anomalies.append("Extreme sea conditions detected")

        # Strong wind anomaly
        if "wind_speed_knots" in df.columns:
            if df["wind_speed_knots"].mean() > 30:
                anomalies.append("Storm-level wind conditions")

        # Fuel consumption spike
        if "fuel_consumption_t_day" in df.columns:
            if df["fuel_consumption_t_day"].max() > df["fuel_consumption_t_day"].mean() * 1.4:
                anomalies.append("Fuel consumption spike detected")

        # Vessel speed anomaly
        if "vessel_speed_knots" in df.columns:
            if df["vessel_speed_knots"].max() > 35:
                anomalies.append("Abnormally high vessel speed")

        if not anomalies:
            anomalies.append("No anomalies detected")

        return anomalies

    except Exception as e:
        return {"error": str(e)}