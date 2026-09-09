def detect_intent(question):

    q = question.lower()

    prediction_keywords = [
        "predict",
        "forecast",
        "future",
        "tomorrow",
        "increase",
        "decrease",
        "trend",
        "prediction"
    ]

    maintenance_keywords = [
        "repair",
        "maintenance",
        "inspect",
        "inspection",
        "service",
        "fix",
        "engine issue",
        "engine problem",
        "cooling system"
    ]

    navigation_keywords = [
        "route",
        "navigation",
        "path",
        "voyage route",
        "safer navigation"
    ]

    operation_keywords = [
        "speed",
        "cruising speed",
        "operational speed"
    ]

    regulation_keywords = [
        "imo",
        "marpol",
        "regulation",
        "cii",
        "eexi",
        "nox",
        "sox",
        "sulphur",
        "carbon intensity"
    ]

    analysis_keywords = [
        "analyze",
        "analysis",
        "report",
        "performance",
        "why",
        "cause",
        "efficiency",
        "anomaly",
        "operational data"
    ]

    if any(word in q for word in prediction_keywords):
        return "prediction"

    if any(word in q for word in maintenance_keywords):
        return "maintenance"

    if any(word in q for word in navigation_keywords):
        return "navigation"

    if any(word in q for word in operation_keywords):
        return "operation"

    if any(word in q for word in regulation_keywords):
        return "knowledge"

    if any(word in q for word in analysis_keywords):
        return "analysis"

    return "analysis"