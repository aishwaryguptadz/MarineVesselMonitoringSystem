import pandas as pd
from .config import DATA_PATH

df = pd.read_csv(DATA_PATH)

def voyage_conditions():

    return {
        "wave_height": df["wave_height_m"].mean(),
        "wind_speed": df["wind_speed_knots"].mean(),
        "sea_temperature": df["sea_temp_c"].mean()
    }