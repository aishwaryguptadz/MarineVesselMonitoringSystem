import pandas as pd
from .voyage_analyzer import get_current_telemetry
from .semantic_engine import detect_metric

ALLOWED_PHYSICAL_FACTORS = [
    "shaft_power_kw", "avg_speed_knots", "rpm", "engine_load_pct",
    "wave_height_m", "wind_speed_knots", "engine_temp_c", "sea_temp_c"
]

def analyze_root_cause(question: str = "", vessel_type: str = None):
    try:
        telemetry = get_current_telemetry(vessel_type)
        df = telemetry["df"]
        latest = telemetry["latest"]
        base = telemetry["baseline_slice"]
        ship_class = telemetry["vessel_type"]
        vessel_label = f" ({ship_class})" if telemetry["is_specific"] else ""
        q_lower = question.lower()

        # Dedicated handler for speed loss under high propulsion
        if "speed" in q_lower and any(w in q_lower for w in ["dropping", "loss", "despite", "falling"]):
            wave = float(latest.get("wave_height_m", 1.2))
            wind = float(latest.get("wind_speed_knots", 10.0))
            load = float(latest.get("engine_load_pct", 50.0))

            reasons = []
            if wave > 1.8:
                reasons.append(f"Significant wave height ({wave:.2f}m) creating severe added hull resistance (ΔRaw)")
            if wind > 18:
                reasons.append(f"Adverse headwind ({wind:.1f} kts) inducing strong aerodynamic drag against {ship_class.lower()} profile")
            if not reasons:
                reasons.append(f"Potential hull fouling or shallow water interaction dissipating effective thrust (Engine load at {load:.1f}%)")
            return reasons

        target = detect_metric(question) if question else "fuel_consumption_t_day"
        if target not in df.columns:
            target = "fuel_consumption_t_day"

        valid_cols = [c for c in ALLOWED_PHYSICAL_FACTORS if c in df.columns and c != target]
        corrs = df[valid_cols + [target]].corr(numeric_only=True)[target].drop(target, errors="ignore")
        strong_influencers = corrs.sort_values(key=abs, ascending=False)

        driving_causes = []
        mitigating_factors = []

        for col, r_val in strong_influencers.items():
            if col not in latest or col not in base.columns:
                continue

            val = float(latest[col])
            mean = float(base[col].mean())
            if mean == 0:
                continue

            delta = ((val - mean) / mean) * 100
            if abs(delta) >= 5.0:
                col_name = col.replace("_", " ").title()
                is_pushing_up = (delta * r_val) > 0

                if is_pushing_up:
                    driving_causes.append(
                        f"{col_name} is elevated by {abs(delta):.1f}% ({val:.1f} vs avg {mean:.1f}), which increases {target.replace('_', ' ')} (r = {r_val:+.2f})."
                    )
                else:
                    mitigating_factors.append(
                        f"{col_name} is lower by {abs(delta):.1f}% ({val:.1f} vs avg {mean:.1f}), which contributes to the reduction in {target.replace('_', ' ')}."
                    )

        readable_target = target.replace('_', ' ')

        if any(w in q_lower for w in ["increase", "high", "spike", "elevated", "excessive"]):
            if driving_causes:
                return driving_causes[:2]
            return [f"Current telemetry shows {readable_target} is operating below voyage baseline{vessel_label}; no upward drivers detected."]

        if any(w in q_lower for w in ["drop", "decrease", "low", "dropping"]):
            if mitigating_factors:
                return mitigating_factors[:2]
            return [f"{readable_target.capitalize()} is running within or above baseline levels; no downward drivers detected."]

        combined = driving_causes if driving_causes else mitigating_factors
        return combined[:2] if combined else [f"All physical telemetry parameters{vessel_label} are within baseline tolerances."]

    except Exception as e:
        return [f"Diagnostics error: {str(e)}"]