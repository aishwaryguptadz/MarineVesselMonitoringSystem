"""
SyntheticAI – Feature Engineering Module
Creates derived features from the cleaned dataset that improve
fuel prediction and route optimisation accuracy.
"""
import os
import pandas as pd
import numpy as np

RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw', 'new_maritime_dataset.csv')
FEATURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'features')


def load_raw_for_features(path: str = RAW_PATH) -> pd.DataFrame:
    """Load original (un-scaled) data for feature engineering."""
    df = pd.read_csv(path)
    print(f"[Features] Loaded raw data: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to the dataframe."""

    # ── Speed efficiency ─────────────────────────────────────────
    df['speed_efficiency'] = np.where(
        df['design_speed_knots'] > 0,
        df['avg_speed_knots'] / df['design_speed_knots'],
        0
    )

    # ── Weather severity ─────────────────────────────────────────
    df['weather_severity'] = (
        df['wind_speed_knots'] + df['wave_height_m'] + df['current_speed_knots']
    )

    # ── Engine efficiency ────────────────────────────────────────
    df['engine_efficiency'] = np.where(
        df['engine_load_pct'] > 0,
        df['shaft_power_kw'] / df['engine_load_pct'],
        0
    )

    # ── Hull drag factor ─────────────────────────────────────────
    df['drag_factor'] = df['hull_fouling_pct'] + df['propeller_fouling_pct']

    # ── Speed cubed (fuel ∝ speed³) ──────────────────────────────
    df['speed_cubed'] = df['avg_speed_knots'] ** 3

    # ── Cargo displacement ratio ─────────────────────────────────
    df['cargo_displacement_ratio'] = np.where(
        df['displacement_tonnes'] > 0,
        df['dwt'] * df['cargo_utilization_pct'] / df['displacement_tonnes'],
        0
    )

    # ── Route-level risk scores ──────────────────────────────────
    for rt in ['moderate', 'safest', 'shortest']:
        storm_col = f'storm_risk_score__{rt}'
        piracy_col = f'piracy_risk_score__{rt}'
        composite_col = f'composite_risk_score__{rt}'
        if all(c in df.columns for c in [storm_col, piracy_col, composite_col]):
            df[f'total_risk__{rt}'] = (
                df[storm_col] + df[piracy_col] + df[composite_col]
            )

    # ── Weather from wx_ columns ─────────────────────────────────
    if 'wx_avg_wind_knots' in df.columns:
        df['wx_severity'] = (
            df['wx_avg_wind_knots'] + df['wx_avg_wave_height_m'] + df['wx_avg_current_speed']
        )

    # ── Regional risk composite ──────────────────────────────────
    if 'region_avg_piracy_risk' in df.columns:
        df['region_total_risk'] = (
            df['region_avg_piracy_risk'] + df['region_avg_storm_prob'] + df['region_avg_ice_prob']
        )

    # ── Vessel age bucket ────────────────────────────────────────
    df['vessel_age_bucket'] = pd.cut(
        df['vessel_age'],
        bins=[0, 5, 10, 15, 20, 100],
        labels=[0, 1, 2, 3, 4]
    ).astype(int)

    # ── Fuel consumption per day efficiency ──────────────────────
    df['fuel_per_day_ratio'] = np.where(
        df['voyage_days'] > 0,
        df['fuel_total_voyage_t'] / df['voyage_days'],
        0
    )

    # ── Days since hull cleaning impact ──────────────────────────
    df['hull_cleaning_urgency'] = np.where(
        df['days_since_hull_cleaning'] > 365, 1, 0
    )

    print(f"[Features] Created {14} derived features")
    return df


def engineer_features(save: bool = True) -> pd.DataFrame:
    """Run the full feature engineering pipeline."""
    print("=" * 60)
    print("  SyntheticAI – Feature Engineering Pipeline")
    print("=" * 60)

    df = load_raw_for_features()
    df = create_derived_features(df)

    if save:
        os.makedirs(FEATURES_DIR, exist_ok=True)
        out_path = os.path.join(FEATURES_DIR, 'feature_engineered_dataset.csv')
        df.to_csv(out_path, index=False)
        print(f"\n[Features] Saved → {out_path}")

    print(f"[Features] Final shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("=" * 60)
    return df


if __name__ == '__main__':
    engineer_features()
