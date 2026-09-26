import numpy as np
import pandas as pd
from .voyage_analyzer import get_current_telemetry

def detect_anomalies(vessel_type: str = None):
    telemetry = get_current_telemetry(vessel_type)
    df = telemetry["df"]
    latest = telemetry["latest"]
    vtype = telemetry["vessel_type"]
    label = f" for {vtype}" if telemetry["is_specific"] else ""

    anomalies = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if col in latest and not pd.isna(latest[col]):
            mean = df[col].mean()
            std = df[col].std()
            val = float(latest[col])
            
            if std > 0:
                z = (val - mean) / std
                if abs(z) >= 2.5:
                    anomalies.append(
                        f"Statistical Outlier{label}: {col.replace('_', ' ').title()} is {abs(z):.2f}σ from mean ({val:.2f} vs avg {mean:.2f})."
                    )

    if not anomalies:
        return [f"All telemetry parameters{label} are within nominal bounds."]

    return anomalies