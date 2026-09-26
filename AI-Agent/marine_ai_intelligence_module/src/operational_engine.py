from .voyage_analyzer import get_current_telemetry

# Hydrodynamic design profiles per ship class
VESSEL_SPEED_PROFILES = {
    "container ship": {"nominal": 19.0, "min_safe": 14.0, "drag_sensitivity": "windage"},
    "tanker":         {"nominal": 12.5, "min_safe": 9.5,  "drag_sensitivity": "wave_slam"},
    "bulk carrier":   {"nominal": 12.0, "min_safe": 9.0,  "drag_sensitivity": "wave_slam"},
    "gas carrier":    {"nominal": 16.0, "min_safe": 12.0, "drag_sensitivity": "boil_off"},
    "general cargo":  {"nominal": 13.5, "min_safe": 10.0, "drag_sensitivity": "general"}
}

def recommended_speed(vessel_type: str = None):
    try:
        telemetry = get_current_telemetry(vessel_type)
        latest = telemetry["latest"]
        ship_class = telemetry["vessel_type"].lower()

        speed = float(latest.get("avg_speed_knots", 12.5))
        fuel = float(latest.get("fuel_consumption_t_day", 40.0))
        wave = float(latest.get("wave_height_m", 1.5))
        wind = float(latest.get("wind_speed_knots", 12.0))

        # Retrieve vessel-class profile
        profile = next((v for k, v in VESSEL_SPEED_PROFILES.items() if k in ship_class), VESSEL_SPEED_PROFILES["bulk carrier"])

        recs = []
        recs.append(f"Vessel Profile: {telemetry['vessel_type']} (Current Speed: {speed:.1f} kts, Fuel Burn: {fuel:.1f} t/day).")

        # Weather impacts conditioned by vessel aerodynamics and displacement
        if "container" in ship_class and wind > 22:
            recs.append(f"Container tier exposure creates high windage drag at {wind:.1f} kts. Speed should be capped at 16.5 kts.")
        elif ("tanker" in ship_class or "bulk" in ship_class) and wave > 2.2:
            recs.append(f"Full-form hull ($C_b > 0.80$) experiences substantial added wave resistance. Limit speed to {max(profile['min_safe'], speed - 1.5):.1f} kts to prevent hull slamming.")
        elif "gas" in ship_class:
            recs.append("Monitor cargo tank pressure: operational speed must balance charter schedule with boil-off gas (BOG) consumption rates.")
        else:
            opt_speed = max(profile["min_safe"], speed - 1.0)
            savings_pct = (1.0 - (opt_speed / speed) ** 3) * 100
            fuel_saved = fuel * (savings_pct / 100)
            recs.append(f"Standard hydrodynamic recommendation: Ease to {opt_speed:.1f} kts.")
            recs.append(f"Admiralty Cubic Law yields ~{fuel_saved:.2f} t/day fuel savings (~{savings_pct:.1f}% reduction).")

        return recs

    except Exception as e:
        return [f"Operational calculation error: {str(e)}"]