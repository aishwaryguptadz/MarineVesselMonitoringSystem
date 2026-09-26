from .router import detect_intent
from .prediction_engine import predict_metric, predict_trends
from .maintenance_engine import maintenance_advice
from .navigation_engine import optimal_route
from .operational_engine import recommended_speed
from .rag_engine import search_regulation
from .anomaly_detector import detect_anomalies
from .root_cause_analyzer import analyze_root_cause
from .semantic_engine import detect_metric
from .voyage_analyzer import voyage_conditions, get_current_telemetry, detect_vessel_context


def answer_question(question: str):
    try:
        vessel_type = detect_vessel_context(question)
        intent = detect_intent(question)
        q_lower = question.lower()

        # 1. KNOWLEDGE & MARITIME ENVIRONMENTAL REGULATIONS
        if intent == "knowledge":
            reg = search_regulation(question)
            return {
                "intent": "knowledge",
                "imo_regulation": reg,
                "answer": reg
            }

        # 2. FULL SYSTEM DIAGNOSTIC REPORT
        if intent == "report":
            telemetry = get_current_telemetry(vessel_type)
            latest = telemetry["latest"]
            anomalies = detect_anomalies(vessel_type)

            if anomalies and "nominal" not in anomalies[0].lower():
                status = "ATTENTION REQUIRED"
                anomaly_summary = anomalies[0]
            else:
                status = "HEALTHY"
                anomaly_summary = "All parameters operating within nominal Gaussian tolerances (all |Z| < 2.0σ)."

            report = (
                f"Voyage Diagnostic Report [{telemetry['vessel_type']} | Status: {status}]\n"
                f"--------------------------------------------------\n"
                f"• Vessel Designation : {telemetry['vessel_type']}\n"
                f"• Vessel Speed       : {latest.get('avg_speed_knots', 'N/A')} knots\n"
                f"• Fuel Consumption   : {latest.get('fuel_consumption_t_day', 'N/A')} tons/day\n"
                f"• Engine Load        : {latest.get('engine_load_pct', 'N/A')}%\n"
                f"• Significant Wave   : {latest.get('wave_height_m', 'N/A')} m\n"
                f"• Wind Telemetry     : {latest.get('wind_speed_knots', 'N/A')} knots\n"
                f"• Anomaly Summary    : {anomaly_summary}"
            )
            return {"intent": "report", "answer": report}

        # 3. ENVIRONMENTAL RESISTANCE & DRAG FACTORS
        if intent == "environmental_resistance":
            telemetry = get_current_telemetry(vessel_type)
            latest = telemetry["latest"]
            wave = float(latest.get("wave_height_m", 1.0))
            wind = float(latest.get("wind_speed_knots", 10.0))
            ship_type = telemetry["vessel_type"]
            header = f" for {ship_type}" if telemetry["is_specific"] else ""

            if wave > 2.2 and wind > 20:
                dominant = f"Combined wave slamming ({wave:.1f}m wave height) and aerodynamic headwind ({wind:.1f} kts)"
            elif "container" in ship_type.lower() and wind > 18:
                dominant = f"Aerodynamic deck cargo windage resistance at {wind:.1f} knots (high profile container tiers)"
            elif wave > 1.5:
                dominant = f"Added wave resistance (ΔRaw) across hull at {wave:.1f}m significant wave height"
            else:
                dominant = f"Headwind friction at {wind:.1f} knots"

            return {
                "intent": "analysis",
                "answer": f"Primary environmental resistance contributor{header}: {dominant}."
            }

        # 4. CURRENT VOYAGE SEA & WEATHER CONDITIONS
        if intent == "conditions":
            conds = voyage_conditions(vessel_type)
            return {
                "intent": "conditions",
                "answer": (
                    f"Current conditions for {conds['vessel_type']}: Wave height is {conds['wave_height']:.2f} m, "
                    f"wind speed is {conds['wind_speed']:.1f} knots, "
                    f"and sea surface temperature is {conds['sea_temperature']:.1f}°C."
                )
            }

        # 5. ROOT CAUSE & DIAGNOSTICS
        if intent == "root_cause":
            drivers = analyze_root_cause(question, vessel_type)
            return {
                "intent": "root_cause",
                "question": question,
                "root_causes": drivers,
                "answer": "Identified operational factors:\n" + "\n".join([f"- {d}" for d in drivers])
            }

        # 6. PREDICTIONS & VOYAGE TREND EXTRAPOLATION
        if intent == "prediction":
            metric = detect_metric(question)
            stats = predict_metric(metric, vessel_type)
            if not stats:
                return {
                    "intent": "prediction",
                    "metric": metric,
                    "message": f"Insufficient telemetry records to project trends for {metric}."
                }

            readable_name = metric.replace("_", " ")
            trend = stats["trend"]
            curr = stats["current_average"]
            pred = stats["predicted_value"]

            if any(w in q_lower for w in ["decrease", "drop", "fall", "slow down", "reduce"]):
                if trend == "decrease":
                    verdict = f"Yes, {readable_name} is expected to decrease from {curr} down to {pred}."
                else:
                    verdict = f"No, {readable_name} is actually trending {trend} (projected at {pred} vs current {curr})."
            else:
                if trend == "increase":
                    verdict = f"Yes, {readable_name} is expected to increase from {curr} to {pred}."
                elif trend == "decrease":
                    verdict = f"No, {readable_name} is expected to decrease from {curr} down to {pred}."
                else:
                    verdict = f"{readable_name.capitalize()} is expected to remain stable around {curr}."

            return {
                "intent": "prediction",
                "metric": metric,
                "current_average": curr,
                "predicted_value": pred,
                "trend": trend,
                "slope": stats.get("slope", 0.0),
                "answer": verdict
            }

        # 7. OPERATIONAL SPEED & HYDRODYNAMIC SAVINGS
        if intent == "operation":
            if any(w in q_lower for w in ["1 knot", "save if", "calculate fuel reduction"]):
                telemetry = get_current_telemetry(vessel_type)
                speed = float(telemetry["latest"].get("avg_speed_knots", 14.0))
                fuel = float(telemetry["latest"].get("fuel_consumption_t_day", 45.0))
                opt_speed = max(8.0, speed - 1.0)
                savings_pct = (1.0 - (opt_speed / speed) ** 3) * 100
                fuel_saved = fuel * (savings_pct / 100)
                return {
                    "intent": "operation",
                    "answer": (
                        f"Reducing speed by 1 knot (from {speed:.1f} to {opt_speed:.1f} kts) saves an estimated "
                        f"{fuel_saved:.2f} tons of fuel per day (~{savings_pct:.1f}% reduction via Admiralty Law: P ∝ V³)."
                    )
                }

            recs = recommended_speed(vessel_type)
            return {
                "intent": "operation",
                "recommended_speed": recs,
                "answer": "\n".join(recs)
            }

        # 8. MACHINERY MAINTENANCE & INSPECTIONS
        if intent == "maintenance":
            advice = maintenance_advice(question, vessel_type)
            return {
                "intent": "maintenance",
                "maintenance_advice": advice,
                "answer": "\n".join([f"- {a}" for a in advice])
            }

        # 9. ROUTE & NAVIGATION
        if intent == "navigation":
            recs = optimal_route(vessel_type)
            return {
                "intent": "navigation",
                "route_recommendation": recs,
                "answer": " ".join(recs)
            }

        # 10. GENERAL ANOMALY AUDIT & OUTLIER SCAN (e.g., Query 91)
        anomalies = detect_anomalies(vessel_type)
        return {
            "intent": "analysis",
            "anomalies": anomalies,
            "answer": f"Operational telemetry check: {anomalies[0]}"
        }

    except Exception as e:
        return {
            "intent": "error",
            "error": str(e),
            "answer": f"Diagnostic processing error: {str(e)}"
        }