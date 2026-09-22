import pandas as pd
from .config import DATA_PATH

df = pd.read_csv(DATA_PATH)

def analyze_dataset():

    return {
        "avg_carbon_emission": round(float(df["co2_emitted_tonnes"].mean()),2),
        "avg_fuel_consumption": round(float(df["fuel_consumption_t_day"].mean()),2),
        "avg_engine_load": round(float(df["engine_load_pct"].mean()),2),
        "avg_speed": round(float(df["avg_speed_knots"].mean()),2),
        "avg_wave_height": round(float(df["wave_height_m"].mean()),2),
        "avg_wind_speed": round(float(df["wind_speed_knots"].mean()),2)
    }