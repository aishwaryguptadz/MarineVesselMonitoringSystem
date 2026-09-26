"""
SyntheticAI – Fuel Consumption Prediction Model (XGBoost)
Trains an XGBoost regressor to predict total voyage fuel consumption.
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))
from feature_engineering import engineer_features

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
EVAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'evaluation')

# ── Feature selection ────────────────────────────────────────────────────
# Core vessel & voyage features for fuel prediction
FEATURE_COLS = [
    # Vessel characteristics
    'dwt', 'vessel_age', 'displacement_tonnes',
    # Voyage parameters
    'distance_nm', 'voyage_days',
    'avg_speed_knots', 'design_speed_knots', 'speed_vs_design_pct',
    # Engine performance
    'engine_load_pct', 'rpm', 'shaft_power_kw', 'sfoc_g_kwh',
    # Cargo & draft
    'cargo_utilization_pct', 'draft_m', 'trim_m',
    'admiralty_coefficient',
    # Weather
    'wind_speed_knots', 'beaufort_number', 'wave_height_m',
    'current_speed_knots', 'seawater_temp_c',
    # Hull condition
    'days_since_hull_cleaning', 'hull_fouling_pct', 'propeller_fouling_pct',
    'turbocharger_efficiency_pct',
    # Fuel properties
    'fuel_quality_index', 'hfo_pct', 'vlsfo_pct', 'mgo_pct', 'lng_pct',
    # Engineered features
    'speed_efficiency', 'weather_severity', 'engine_efficiency',
    'drag_factor', 'speed_cubed', 'cargo_displacement_ratio',
    'wx_severity', 'region_total_risk', 'vessel_age_bucket',
    'hull_cleaning_urgency',
]

TARGET_COL = 'fuel_total_voyage_t'


def prepare_data():
    """Load feature-engineered data and split into train/test."""
    df = engineer_features(save=True)

    # Encode categoricals that model needs
    from sklearn.preprocessing import LabelEncoder
    cat_cols_for_model = ['ship_type', 'loading_condition', 'fuel_type', 'current_direction', 'route']
    for col in cat_cols_for_model:
        if col in df.columns:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))

    # Add encoded categoricals to features
    extra_cols = [c + '_encoded' for c in cat_cols_for_model if c + '_encoded' in df.columns]
    feature_cols = [c for c in FEATURE_COLS + extra_cols if c in df.columns]

    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()

    # Handle any remaining NaN/inf
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[Fuel Model] Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"[Fuel Model] Features: {len(feature_cols)}")
    return X_train, X_test, y_train, y_test, feature_cols


def train_model(X_train, y_train, tune: bool = True):
    """Train XGBoost with optional hyperparameter tuning."""
    if tune:
        print("[Fuel Model] Running GridSearchCV (this may take a few minutes)...")
        param_grid = {
            'n_estimators': [200, 400],
            'max_depth': [5, 7, 9],
            'learning_rate': [0.05, 0.1],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0],
        }
        xgb = XGBRegressor(
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1,
        )
        grid = GridSearchCV(
            xgb, param_grid,
            cv=3, scoring='r2',
            verbose=1, n_jobs=-1,
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_
        print(f"[Fuel Model] Best params: {grid.best_params_}")
        print(f"[Fuel Model] Best CV R²: {grid.best_score_:.4f}")
    else:
        best_model = XGBRegressor(
            n_estimators=400, max_depth=7, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            objective='reg:squarederror', random_state=42, n_jobs=-1,
        )
        best_model.fit(X_train, y_train)

    return best_model


def evaluate_model(model, X_test, y_test, feature_cols):
    """Evaluate and generate reports."""
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

    print("\n" + "=" * 50)
    print("  FUEL MODEL EVALUATION")
    print("=" * 50)
    print(f"  MAE:  {mae:.2f} tonnes")
    print(f"  RMSE: {rmse:.2f} tonnes")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  R²:   {r2:.4f}")
    print("=" * 50)

    # ── Save plots ────────────────────────────────────────────────
    os.makedirs(EVAL_DIR, exist_ok=True)

    # Actual vs Predicted
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_test, y_pred, alpha=0.4, s=10)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    ax.set_xlabel('Actual Fuel (tonnes)')
    ax.set_ylabel('Predicted Fuel (tonnes)')
    ax.set_title(f'Fuel Model: Actual vs Predicted (R²={r2:.4f})')
    fig.savefig(os.path.join(EVAL_DIR, 'fuel_actual_vs_predicted.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Feature importance (top 20)
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)[-20:]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(sorted_idx)), importance[sorted_idx])
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_cols[i] for i in sorted_idx])
    ax.set_xlabel('Feature Importance')
    ax.set_title('Fuel Model: Top 20 Feature Importances')
    fig.savefig(os.path.join(EVAL_DIR, 'fuel_feature_importance.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"[Fuel Model] Plots saved → {EVAL_DIR}/")
    return {'mae': mae, 'rmse': rmse, 'mape': mape, 'r2': r2}


def main(tune: bool = True):
    """Full fuel model training pipeline."""
    print("\n" + "=" * 60)
    print("  SyntheticAI – Fuel Prediction Model Training")
    print("=" * 60)

    X_train, X_test, y_train, y_test, feature_cols = prepare_data()
    model = train_model(X_train, y_train, tune=tune)
    metrics = evaluate_model(model, X_test, y_test, feature_cols)

    # Save model & feature list
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, 'fuel_model.pkl'))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, 'fuel_feature_cols.pkl'))
    print(f"[Fuel Model] Model saved → {MODELS_DIR}/fuel_model.pkl")

    return model, metrics


if __name__ == '__main__':
    # Use --fast flag to skip GridSearch for quick testing
    fast = '--fast' in sys.argv
    main(tune=not fast)
