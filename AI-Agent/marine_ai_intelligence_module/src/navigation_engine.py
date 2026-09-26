from .voyage_analyzer import get_current_telemetry

def optimal_route(vessel_type: str = None):
    try:
        telemetry = get_current_telemetry(vessel_type)
        latest = telemetry["latest"]
        ship = telemetry["vessel_type"]
        wave = float(latest.get("wave_height_m", 1.2))
        wind = float(latest.get("wind_speed_knots", 12.0))

        advisories = []

        # Weather routing recommendations
        if wave > 2.5:
            advisories.append(f"Heavy Weather Advisory ({ship}): Significant wave height at {wave:.1f}m. Alter route heading 12° south to avoid deep wave troughs and structural slamming.")
        elif wind > 24.0:
            advisories.append(f"High Wind Corridor ({ship}): True wind at {wind:.1f} kts. Recommended route diversion around windward passage to reduce beam drift and aerodynamic resistance.")
        else:
            advisories.append(f"Direct Route Optimal ({ship}): Calm conditions logged ({wave:.1f}m waves, {wind:.1f} kts wind). Great Circle route track recommended.")

        # Class-specific hydrodynamic navigation guidance
        ship_lower = ship.lower()
        if "container" in ship_lower:
            advisories.append("Maintain track angle to avoid synchronous and parametric rolling in quartering seas.")
        elif "bulk" in ship_lower or "tanker" in ship_lower:
            advisories.append("Optimize dynamic ballast trim by the stern (0.8m) to lower hull skin friction on active track.")
        elif "gas" in ship_lower:
            advisories.append("Plan routing to account for ambient sea temperature impacts on cargo boil-off containment.")

        return advisories

    except Exception as e:
        return [f"Navigation analysis error: {str(e)}"]