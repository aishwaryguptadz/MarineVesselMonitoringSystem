import pandas as pd
from .config import DATA_PATH


def optimal_route():

    try:
        df = pd.read_csv(DATA_PATH)

        recommendations = []

        # Check wave conditions
        if "wave_height_m" in df.columns:
            if df["wave_height_m"].mean() > 3:
                recommendations.append("Avoid high wave regions to maintain vessel stability")

        # Check wind conditions
        if "wind_speed_knots" in df.columns:
            if df["wind_speed_knots"].mean() > 20:
                recommendations.append("Adjust route to reduce strong wind resistance")

        # Check vessel speed
        if "vessel_speed_knots" in df.columns:
            if df["vessel_speed_knots"].mean() > 28:
                recommendations.append("Reduce cruising speed to improve fuel efficiency")

        # Check fuel consumption
        if "fuel_consumption_t_day" in df.columns:
            if df["fuel_consumption_t_day"].mean() > 25:
                recommendations.append("Select route with calmer sea conditions to reduce fuel usage")

        if not recommendations:
            recommendations.append("Current route conditions appear optimal")

        return recommendations

    except Exception as e:
        return {"error": str(e)}