import pandas as pd
from .config import DATA_PATH

df = pd.read_csv(DATA_PATH)


def compute_correlations():

    if "fuel_consumption_t_day" not in df.columns:
        return {"error": "fuel_consumption_t_day column not found in dataset"}

    # Compute correlation matrix
    corr_matrix = df.corr(numeric_only=True)

    # Extract correlations with fuel consumption
    fuel_corr = corr_matrix["fuel_consumption_t_day"].drop("fuel_consumption_t_day")

    # Remove weak correlations
    fuel_corr = fuel_corr[abs(fuel_corr) > 0.2]

    # Sort by strongest relationship
    fuel_corr = fuel_corr.sort_values(ascending=False)

    return fuel_corr.to_dict()