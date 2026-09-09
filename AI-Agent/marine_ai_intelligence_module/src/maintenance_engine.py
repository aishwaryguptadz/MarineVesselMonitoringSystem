import pandas as pd
from .config import DATA_PATH


def maintenance_advice():

    try:
        df = pd.read_csv(DATA_PATH)

        advice = []

        # Engine load check
        if "engine_load_pct" in df.columns:
            if df["engine_load_pct"].mean() > 80:
                advice.append("Inspect engine cooling system due to high engine load")

        # Engine temperature check
        if "engine_temp_c" in df.columns:
            if df["engine_temp_c"].mean() > 95:
                advice.append("Check engine cooling system and coolant levels")

        # Engine vibration check
        if "engine_vibration" in df.columns:
            if df["engine_vibration"].mean() > 7:
                advice.append("Inspect engine mounts and rotating components")

        # Fuel system check
        if "fuel_consumption_t_day" in df.columns:
            if df["fuel_consumption_t_day"].max() > df["fuel_consumption_t_day"].mean() * 1.4:
                advice.append("Inspect fuel injectors for inefficiency")

        if not advice:
            advice.append("Engine operating normally")

        return advice

    except Exception as e:
        return {"error": str(e)}