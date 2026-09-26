import pandas as pd
from .config import DATA_PATH

df = pd.read_csv(DATA_PATH)

VESSEL_TYPES = [
    "tanker", "bulk carrier", "general cargo", "container ship", "gas carrier", "lng", "lpg"
]

def detect_vessel_context(question: str):
    q = question.lower()
    for vtype in VESSEL_TYPES:
        if vtype in q:
            if vtype in ["lng", "lpg"]:
                return "gas carrier"
            return vtype
    return None

def get_current_telemetry(vessel_type: str = None):
    global df
    data_view = df

    type_col = None
    for candidate in ["vessel_type", "ship_type", "type", "cargo_type"]:
        if candidate in df.columns:
            type_col = candidate
            break

    # If user explicitly asked for a ship type, filter strictly to that class
    if type_col and vessel_type:
        filtered = df[df[type_col].astype(str).str.lower().str.contains(vessel_type.lower())]
        if not filtered.empty:
            data_view = filtered
            display_name = vessel_type.title()
        else:
            display_name = vessel_type.title()
    else:
        # If user did NOT ask for a ship type, do NOT pretend it's a Bulk Carrier
        display_name = "Vessel"

    total = len(data_view)
    window = min(30, total)
    current_slice = data_view.tail(window)
    baseline_slice = data_view.iloc[:-window] if total > window else data_view
    latest = data_view.iloc[-1].to_dict()

    return {
        "df": data_view,
        "current_slice": current_slice,
        "baseline_slice": baseline_slice,
        "latest": latest,
        "vessel_type": display_name,
        "is_specific": (vessel_type is not None)
    }

get_voyage_telemetry = get_current_telemetry

def voyage_conditions(vessel_type: str = None):
    telemetry = get_current_telemetry(vessel_type)
    latest = telemetry["latest"]
    cur = telemetry["current_slice"]

    label = telemetry["vessel_type"] if telemetry["is_specific"] else "Active Voyage"

    return {
        "vessel_type": label,
        "wave_height": float(latest.get("wave_height_m", cur["wave_height_m"].mean() if "wave_height_m" in cur else 1.5)),
        "wind_speed": float(latest.get("wind_speed_knots", cur["wind_speed_knots"].mean() if "wind_speed_knots" in cur else 12.0)),
        "sea_temperature": float(latest.get("sea_temp_c", cur["sea_temp_c"].mean() if "sea_temp_c" in cur else 18.0))
    }