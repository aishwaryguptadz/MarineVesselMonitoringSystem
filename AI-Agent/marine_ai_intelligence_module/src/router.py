def detect_intent(question: str) -> str:
    q = question.lower().strip()

    # 1. Full Diagnostic Reports
    if any(k in q for k in ["diagnostic report", "performance report", "system diagnostic"]):
        return "report"

    # 2. Maritime Regulations & Statutory Compliance
    if any(k in q for k in [
        "imo", "marpol", "cii", "eexi", "nox", "sox", "sulphur", "sulfur",
        "regulation", "ets", "dcs", "ballast", "discharge", "annex", "carbon intensity"
    ]):
        return "knowledge"

    # 3. Diagnostic Root Cause ("why", "cause", "driving up", "spike")
    if any(k in q for k in [
        "why", "cause", "causes", "reason", "due to", "driving up",
        "spike", "dropping despite", "abnormal fuel burn"
    ]):
        return "root_cause"

    # 4. Predictions & Trends
    if any(k in q for k in ["predict", "forecast", "future", "tomorrow", "trend", "will "]):
        return "prediction"

    # 5. Speed, Propulsion Operational Adjustments & Fuel Savings
    # Place BEFORE conditions so "reduce speed in current sea conditions" -> operation
    if any(k in q for k in [
        "speed", "reduce speed", "operating speed", "cruising speed", "slow down",
        "knots", "rpm", "fuel reduction", "economically efficient", "ease propulsion",
        "counter wave slamming", "speed profile", "save if we drop"
    ]):
        return "operation"

    # 6. Route Navigation & Diverting
    # Place BEFORE conditions so "safer navigation route given current sea states" -> navigation
    if any(k in q for k in [
        "route", "navigation", "divert", "track", "waypoint",
        "head currents", "quartering seas", "routing adjustments"
    ]):
        return "navigation"

    # 7. Environmental Resistance
    if any(k in q for k in ["resistance", "contributing most"]):
        return "environmental_resistance"

    # 8. Pure Weather & Sea Condition Inquiries (Stand-alone weather requests)
    if any(k in q for k in [
        "sea and wind conditions", "current voyage sea and wind", "sea conditions",
        "weather conditions", "current conditions", "sea state"
    ]):
        return "conditions"

    # 9. Machinery Maintenance & Subsystems
    if any(k in q for k in [
        "maintenance", "repair", "inspect", "service", "vibration", "injector",
        "servicing", "cooling", "temperatures", "exhaust", "turbocharger",
        "scavenge", "heat exchanger", "bearing", "boiler", "reliquefaction",
        "inert gas", "compressor", "cargo heating"
    ]):
        return "maintenance"

    # 10. Default: Telemetry Outlier & Bounds Audit
    return "analysis"