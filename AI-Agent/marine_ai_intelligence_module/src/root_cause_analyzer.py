import pandas as pd
from .config import DATA_PATH


def analyze_root_cause():

    try:
        df = pd.read_csv(DATA_PATH)

        causes = []

        # Engine load cause
        if "engine_load_pct" in df.columns:
            if df["engine_load_pct"].mean() > 80:
                causes.append("Engine running near maximum capacity")

        # Wave impact
        if "wave_height_m" in df.columns:
            if df["wave_height_m"].mean() > 3:
                causes.append("Severe sea state increasing propulsion demand")

        # Wind resistance
        if "wind_speed_knots" in df.columns:
            if df["wind_speed_knots"].mean() > 20:
                causes.append("Strong winds increasing vessel resistance")

        # Fuel consumption cause
        if "fuel_consumption_t_day" in df.columns:
            if df["fuel_consumption_t_day"].mean() > 25:
                causes.append("High propulsion demand increasing fuel consumption")

        # Vessel speed cause
        if "vessel_speed_knots" in df.columns:
            if df["vessel_speed_knots"].mean() > 28:
                causes.append("High cruising speed increasing fuel burn")

        if not causes:
            causes.append("No significant root causes detected")

        return causes

    except Exception as e:
        return {"error": str(e)}