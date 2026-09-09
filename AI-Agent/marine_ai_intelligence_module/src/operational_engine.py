import pandas as pd
from .config import DATA_PATH


def recommended_speed():

    try:
        df = pd.read_csv(DATA_PATH)

        recommendations = []

        # Rough sea conditions
        if "wave_height_m" in df.columns:
            if df["wave_height_m"].mean() > 3:
                recommendations.append("Maintain 12–14 knots due to rough sea conditions")

        # Strong wind
        if "wind_speed_knots" in df.columns:
            if df["wind_speed_knots"].mean() > 20:
                recommendations.append("Reduce speed to 12–15 knots to reduce wind resistance")

        # High engine load
        if "engine_load_pct" in df.columns:
            if df["engine_load_pct"].mean() > 80:
                recommendations.append("Reduce speed slightly to reduce engine stress")

        # High fuel consumption
        if "fuel_consumption_t_day" in df.columns:
            if df["fuel_consumption_t_day"].mean() > 25:
                recommendations.append("Lower cruising speed by 1–2 knots to improve fuel efficiency")

        if not recommendations:
            recommendations.append("Maintain normal cruising speed (14–18 knots)")

        return recommendations

    except Exception as e:
        return {"error": str(e)}