from .router import detect_intent
from .prediction_engine import predict_metric
from .maintenance_engine import maintenance_advice
from .navigation_engine import optimal_route
from .operational_engine import recommended_speed
from .rag_engine import search_regulation
from .anomaly_detector import detect_anomalies
from .root_cause_analyzer import analyze_root_cause
from .semantic_engine import detect_metric
from .voyage_analyzer import voyage_conditions


def generate_report(data=None, causes=None, anomalies=None):
    """
    Generates a structured engineering report string from telemetry inputs.
    """
    data = data or {}
    causes = causes or []
    anomalies = anomalies or []

    report = "=== Ship Intelligence & Voyage Diagnostic Report ===\n\n"

    report += "Operational Metrics:\n"
    if isinstance(data, dict):
        for k, v in data.items():
            report += f"  • {k.replace('_', ' ').capitalize()}: {v}\n"
    else:
        report += f"  {data}\n"

    report += "\nDetected Anomalies:\n"
    if anomalies:
        for a in anomalies:
            if isinstance(a, dict):
                report += f"  • [{a.get('severity', 'INFO')}] {a.get('summary', str(a))}\n"
            else:
                report += f"  • {a}\n"
    else:
        report += "  • None detected within baseline tolerances.\n"

    report += "\nIdentified Root Causes / Parametric Drivers:\n"
    if causes:
        for c in causes:
            report += f"  • {c}\n"
    else:
        report += "  • Nominal operation; no abnormal driving factors found.\n"

    return report


def answer_question(question: str):
    try:
        intent = detect_intent(question)

        # 1. PREDICTION INTENT
        if intent == "prediction":
            metric = detect_metric(question)
            calc = predict_metric(metric)
            if not calc:
                return {"answer": f"Insufficient numerical telemetry to compute trend for '{metric}'."}

            metric_name = metric.replace('_', ' ')
            if calc['trend'] == "increase":
                explanation = f"Yes, {metric_name} is projected to increase based on current voyage acceleration."
            elif calc['trend'] == "decrease":
                explanation = f"No, {metric_name} is projected to decrease according to negative OLS slope."
            else:
                explanation = f"{metric_name.capitalize()} is projected to remain stable along the current voyage profile."

            return {
                "intent": "prediction",
                "metric": metric,
                "current_val": calc["current_value"],
                "projected_val": calc["predicted_value"],
                "slope": calc["slope_per_hour"],
                "rate_of_change": f"{calc['projected_change_pct']:+0.2f}%",
                "trend": calc["trend"],
                "answer": (
                    f"{explanation} (Current: {calc['current_value']}, "
                    f"Projected: {calc['predicted_value']}, Rate: {calc['projected_change_pct']:+0.2f}%, "
                    f"Linear Slope: {calc['slope_per_hour']:+.4f} units/step)."
                )
            }

        # 2. ROOT CAUSE INTENT
        if intent == "root_cause":
            causes = analyze_root_cause()
            return {
                "intent": "root_cause",
                "query": question,
                "diagnostics": causes,
                "answer": "Identified operational drivers:\n" + "\n".join([f"• {c}" for c in causes])
            }

        # 3. OPERATION INTENT
        if intent == "operation":
            recs = recommended_speed()
            return {
                "intent": "operation",
                "admiralty_assessment": recs,
                "answer": "\n".join(recs)
            }

        # 4. MAINTENANCE INTENT
        if intent == "maintenance":
            diagnostics = maintenance_advice()
            return {
                "intent": "maintenance",
                "machinery_status": diagnostics,
                "answer": "\n".join([f"• {d}" for d in diagnostics])
            }

        # 5. NAVIGATION INTENT
        if intent == "navigation":
            cond = voyage_conditions()
            recs = optimal_route()
            return {
                "intent": "navigation",
                "conditions": cond,
                "recommendations": recs,
                "answer": f"Voyage sea state: wave {cond['current_wave_height_m']}m, wind {cond['current_wind_speed_knots']} kts. Advisory: " + " ".join(recs)
            }

        # 6. REGULATORY KNOWLEDGE INTENT
        if intent == "knowledge":
            reg = search_regulation(question)
            return {
                "intent": "knowledge",
                "regulation_extract": reg,
                "answer": reg
            }

        # 7. GENERAL ANALYSIS
        anomalies = detect_anomalies()
        causes = analyze_root_cause()
        return {
            "intent": "analysis",
            "telemetry_anomalies": anomalies,
            "root_causes": causes,
            "answer": f"Voyage Telemetry Audit: Detected {len(anomalies)} point deviations. Dominant driver: {causes[0]}"
        }

    except Exception as e:
        return {"error": "Processing failed", "details": str(e)}