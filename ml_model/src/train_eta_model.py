"""
SyntheticAI – ETA Prediction Model (Random Forest)
Trains a Random Forest regressor to predict voyage duration in hours.
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from feature_engineering import engineer_features

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
EVAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'evaluation')

# ── Features for ETA prediction ──────────────────────────────────────────
FEATURE_COLS = [
    # Route / speed
    'distance_nm', 'avg_speed_knots', 'design_speed_knots', 'speed_vs_design_pct',
    # Engine
    'engine_load_pct', 'rpm', 'shaft_power_kw',
    # Weather
    'wind_speed_knots', 'beaufort_number', 'wave_height_m',
    'current_speed_knots', 'seawater_temp_c',
    # Vessel
    'dwt', 'vessel_age', 'displacement_tonnes',
    'draft_m', 'trim_m', 'cargo_utilization_pct',
    # Hull
    'hull_fouling_pct', 'propeller_fouling_pct',
    'days_since_hull_cleaning',
    # Engineered
    'speed_efficiency', 'weather_severity', 'engine_efficiency',
    'drag_factor', 'wx_severity', 'vessel_age_bucket',
]

TARGET_COL = 'voyage_hours'


def prepare_data():
    """Load feature-engineered data and split."""
    df = engineer_features(save=False)

    from sklearn.preprocessing import LabelEncoder
    cat_cols_for_model = ['ship_type', 'loading_condition', 'current_direction', 'route']
    for col in cat_cols_for_model:
        if col in df.columns:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))

    extra_cols = [c + '_encoded' for c in cat_cols_for_model if c + '_encoded' in df.columns]
    feature_cols = [c for c in FEATURE_COLS + extra_cols if c in df.columns]

    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[ETA Model] Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"[ETA Model] Features: {len(feature_cols)}")
    return X_train, X_test, y_train, y_test, feature_cols


def train_model(X_train, y_train, tune: bool = True):
    """Train Random Forest with optional hyperparameter tuning."""
    if tune:
        print("[ETA Model] Running GridSearchCV...")
        param_grid = {
            'n_estimators': [200, 400],
            'max_depth': [10, 15, 20],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2],
        }
        rf = RandomForestRegressor(random_state=42, n_jobs=-1)
        grid = GridSearchCV(
            rf, param_grid,
            cv=3, scoring='r2',
            verbose=1, n_jobs=-1,
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_
        print(f"[ETA Model] Best params: {grid.best_params_}")
        print(f"[ETA Model] Best CV R²: {grid.best_score_:.4f}")
    else:
        best_model = RandomForestRegressor(
            n_estimators=400, max_depth=15,
            min_samples_split=2, min_samples_leaf=1,
            random_state=42, n_jobs=-1,
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
    print("  ETA MODEL EVALUATION")
    print("=" * 50)
    print(f"  MAE:  {mae:.2f} hours ({mae/24:.1f} days)")
    print(f"  RMSE: {rmse:.2f} hours ({rmse/24:.1f} days)")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  R²:   {r2:.4f}")
    print("=" * 50)

    os.makedirs(EVAL_DIR, exist_ok=True)

    # Actual vs Predicted
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_test, y_pred, alpha=0.4, s=10)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    ax.set_xlabel('Actual Voyage Hours')
    ax.set_ylabel('Predicted Voyage Hours')
    ax.set_title(f'ETA Model: Actual vs Predicted (R²={r2:.4f})')
    fig.savefig(os.path.join(EVAL_DIR, 'eta_actual_vs_predicted.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Feature importance (top 20)
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)[-20:]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(sorted_idx)), importance[sorted_idx])
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_cols[i] for i in sorted_idx])
    ax.set_xlabel('Feature Importance')
    ax.set_title('ETA Model: Top 20 Feature Importances')
    fig.savefig(os.path.join(EVAL_DIR, 'eta_feature_importance.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"[ETA Model] Plots saved → {EVAL_DIR}/")
    return {'mae': mae, 'rmse': rmse, 'mape': mape, 'r2': r2}


def main(tune: bool = True):
    """Full ETA model training pipeline."""
    print("\n" + "=" * 60)
    print("  SyntheticAI – ETA Prediction Model Training")
    print("=" * 60)

    X_train, X_test, y_train, y_test, feature_cols = prepare_data()
    model = train_model(X_train, y_train, tune=tune)
    metrics = evaluate_model(model, X_test, y_test, feature_cols)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, 'eta_model.pkl'))
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, 'eta_feature_cols.pkl'))
    print(f"[ETA Model] Model saved → {MODELS_DIR}/eta_model.pkl")

    return model, metrics


if __name__ == '__main__':
    fast = '--fast' in sys.argv
    main(tune=not fast)
