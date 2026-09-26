"""
SyntheticAI – Data Preprocessing Module
Cleans raw maritime dataset: handles missing values, encodes categoricals,
normalises numerics, and saves a clean CSV for downstream use.
"""
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# ── paths ──────────────────────────────────────────────────────────────────
RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'new_maritime_dataset.csv')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

# Categorical columns that need encoding
CATEGORICAL_COLS = [
    'ship_type', 'loading_condition', 'fuel_type', 'current_direction',
    'route', 'nox_tier', 'cii_flag_state', 'cii_classification_society',
    'cii_primary_fuel_type', 'cii_cii_rating', 'cii_prev_year_cii_rating',
    'efficiency_rating',
]

# Port / region columns (will be label-encoded separately)
PORT_COLS = [
    'origin_port__moderate', 'origin_port__safest', 'origin_port__shortest',
    'destination_port__moderate', 'destination_port__safest', 'destination_port__shortest',
    'origin_region__moderate', 'origin_region__safest', 'origin_region__shortest',
]

# ID / name columns to drop (not useful for training)
DROP_COLS = [
    'master_record_id', 'vessel_id', 'cii_vessel_name',
]


def load_raw_data(path: str = RAW_PATH) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    df = pd.read_csv(path)
    print(f"[Preprocessing] Loaded raw data: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values – median for numeric, mode for categorical."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  → Filled {col} nulls with median ({median_val:.4f})")

    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            print(f"  → Filled {col} nulls with mode ({mode_val})")

    print(f"[Preprocessing] Missing values handled. Remaining nulls: {df.isnull().sum().sum()}")
    return df


def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop ID / name columns not useful for modelling."""
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    print(f"[Preprocessing] Dropped columns: {cols_to_drop}")
    return df


def encode_categoricals(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Label-encode categorical and port columns. Returns df + encoder dict."""
    encoders = {}

    all_cat = [c for c in CATEGORICAL_COLS + PORT_COLS if c in df.columns]
    for col in all_cat:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"  → Encoded {col} ({len(le.classes_)} classes)")

    print(f"[Preprocessing] Encoded {len(all_cat)} categorical columns")
    return df, encoders


def normalise_numerics(df: pd.DataFrame) -> tuple[pd.DataFrame, StandardScaler]:
    """Standard-scale all numeric columns (except binary 0/1 flags)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Skip binary columns (only 0 and 1)
    binary_cols = [c for c in numeric_cols if set(df[c].dropna().unique()).issubset({0, 1, 0.0, 1.0})]
    cols_to_scale = [c for c in numeric_cols if c not in binary_cols]

    scaler = StandardScaler()
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

    print(f"[Preprocessing] Scaled {len(cols_to_scale)} numeric columns (skipped {len(binary_cols)} binary)")
    return df, scaler


def preprocess(save: bool = True) -> pd.DataFrame:
    """Run the full preprocessing pipeline."""
    print("=" * 60)
    print("  SyntheticAI – Data Preprocessing Pipeline")
    print("=" * 60)

    df = load_raw_data()
    df = handle_missing_values(df)
    df = drop_irrelevant_columns(df)
    df, encoders = encode_categoricals(df)
    df, scaler = normalise_numerics(df)

    if save:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        os.makedirs(MODELS_DIR, exist_ok=True)

        out_path = os.path.join(PROCESSED_DIR, 'cleaned_dataset.csv')
        df.to_csv(out_path, index=False)
        print(f"\n[Preprocessing] Saved cleaned data → {out_path}")

        # Save encoders & scaler for inference
        joblib.dump(encoders, os.path.join(MODELS_DIR, 'label_encoders.pkl'))
        joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
        print("[Preprocessing] Saved encoders & scaler → models/")

    print(f"[Preprocessing] Final shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("=" * 60)
    return df


if __name__ == '__main__':
    preprocess()
