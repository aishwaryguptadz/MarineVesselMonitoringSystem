"""
SyntheticAI – Prediction Service
Loads trained models and provides prediction + route recommendation API.
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from route_optimizer import RouteOptimizer
from feature_engineering import create_derived_features

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw', 'new_maritime_dataset.csv')


HEALTH_LIMITS = {
    #  input key             (good, bad)    meaning
    'rpm':                   (110, 150),    # engine speed, rev/min
    'engineTemp':            (75, 105),     # jacket-water temperature, deg C
    'vibration':             (2.8, 11.0),   # RMS velocity, mm/s
    'engineLoadPct':         (85, 110),     # % of maximum continuous rating
    'turbochargerEffPct':    (80, 60),      # %, higher is better
    'hullFoulingPct':        (20, 100),     # %
    'propellerFoulingPct':   (15, 100),     # %
}
HEALTH_WEIGHTS = {
    'rpm': 0.15, 'engineTemp': 0.20, 'vibration': 0.20, 'engineLoadPct': 0.10,
    'turbochargerEffPct': 0.15, 'hullFoulingPct': 0.10, 'propellerFoulingPct': 0.10,
}

PROFILE_COLUMNS = {
    'rpm': 'rpm',
    'jacket_water_temp_c': 'engineTemp',
    'engine_load_pct': 'engineLoadPct',
    'turbocharger_efficiency_pct': 'turbochargerEffPct',
    'hull_fouling_pct': 'hullFoulingPct',
    'propeller_fouling_pct': 'propellerFoulingPct',
}

LEGACY_LOAD_REFERENCE_T = 5000.0    # old API field `loadWeight` (tonnes) -> % load
ROUTE_RISK_PENALTY_MAX = 10.0       # max health points removed for a risky route
REMAINING_LIFE_MAX_HOURS = 200.0    # remaining life at 100 % health


def _linear_score(value: float, good: float, bad: float) -> float:
    """1.0 at/inside `good`, 0.0 at/beyond `bad`, linear in between."""
    return float(np.clip(1.0 - (value - good) / (bad - good), 0.0, 1.0))


class MaritimePredictor:
    """Load trained models and make fuel/ETA predictions + route recommendations."""

    def __init__(self):
        self.fuel_model = None
        self.eta_model = None
        self.fuel_features = None
        self.eta_features = None
        self.optimizer = None
        self._profile_df = None
        self._load_models()

    def _load_models(self):
        """Load saved models if available."""
        fuel_path = os.path.join(MODELS_DIR, 'fuel_model.pkl')
        eta_path = os.path.join(MODELS_DIR, 'eta_model.pkl')

        if os.path.exists(fuel_path):
            self.fuel_model = joblib.load(fuel_path)
            self.fuel_features = joblib.load(os.path.join(MODELS_DIR, 'fuel_feature_cols.pkl'))
            print("[Predictor] Fuel model loaded ✓")
        else:
            print("[Predictor] ⚠ Fuel model not found. Train it first:")
            print("            python src/train_fuel_model.py")

        if os.path.exists(eta_path):
            self.eta_model = joblib.load(eta_path)
            self.eta_features = joblib.load(os.path.join(MODELS_DIR, 'eta_feature_cols.pkl'))
            print("[Predictor] ETA model loaded ✓")
        else:
            print("[Predictor] ⚠ ETA model not found. Train it first:")
            print("            python src/train_eta_model.py")

        self.optimizer = RouteOptimizer(RAW_PATH)
        print("[Predictor] Route optimizer loaded ✓")

        # Per-ship sensor data used by the health model
        self._profile_df = pd.read_csv(
            RAW_PATH, usecols=['vessel_id', 'ship_type', *PROFILE_COLUMNS.keys()]
        )
        print("[Predictor] Health profiles loaded ✓")

    def predict_fuel(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict fuel consumption given a feature dataframe."""
        if self.fuel_model is None:
            raise RuntimeError("Fuel model not loaded. Train it first.")
        X = features_df[self.fuel_features].copy()
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        return self.fuel_model.predict(X)

    def predict_eta(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict voyage hours given a feature dataframe."""
        if self.eta_model is None:
            raise RuntimeError("ETA model not loaded. Train it first.")
        X = features_df[self.eta_features].copy()
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        return self.eta_model.predict(X)

    # ── Health ───────────────────────────────────────────────────────────
    @staticmethod
    def alert_level(health_score: float) -> str:
        """Single source of truth for alert thresholds (score is 0-100)."""
        if health_score >= 80:
            return "HEALTHY"
        if health_score >= 50:
            return "WARNING"
        return "CRITICAL"

    def predict_health(self, data: dict) -> float:
        """
        Engine health index on a 0-100 scale (100 = perfect).

        Accepted keys (all optional, at least one required):
            rpm, engineTemp, vibration, engineLoadPct,
            turbochargerEffPct, hullFoulingPct, propellerFoulingPct
        Legacy key `loadWeight` (tonnes) is still accepted.
        """
        readings = {k: data[k] for k in HEALTH_LIMITS if data.get(k) is not None}

        if 'engineLoadPct' not in readings and data.get('loadWeight') is not None:
            readings['engineLoadPct'] = data['loadWeight'] / LEGACY_LOAD_REFERENCE_T * 100.0

        if not readings:
            raise ValueError("No sensor readings supplied for health prediction.")

        total_w = sum(HEALTH_WEIGHTS[k] for k in readings)
        score = sum(
            HEALTH_WEIGHTS[k] * _linear_score(float(v), *HEALTH_LIMITS[k])
            for k, v in readings.items()
        ) / total_w

        return round(score * 100.0, 2)

    def get_ship_profile(self, ship_type: str = None, vessel_id=None) -> dict:
        """Average sensor readings for a ship type (and optionally one vessel)."""
        if self._profile_df is None:
            raise RuntimeError("Health profile data not loaded.")

        df = self._profile_df
        if vessel_id is not None:
            df = df[df['vessel_id'].astype(str) == str(vessel_id)]
        if ship_type:
            df = df[df['ship_type'].str.lower() == ship_type.strip().lower()]
        if df.empty:
            raise ValueError(
                f"No data for ship_type={ship_type!r}, vessel_id={vessel_id!r}."
            )

        profile = {}
        for col, key in PROFILE_COLUMNS.items():
            series = df[col]
            if key.endswith('FoulingPct'):
                series = series.clip(lower=0)      # dataset has small negatives
            profile[key] = round(float(series.mean()), 2)
        profile['records_used'] = int(len(df))
        return profile

    def predict_voyage_health(self, ship_type: str = None, route: dict = None,
                              vessel_id=None) -> dict:
        """Health for a chosen ship type on a chosen route (both change the score)."""
        profile = self.get_ship_profile(ship_type, vessel_id)
        engine_health = self.predict_health(profile)

        risk = float((route or {}).get('avg_risk_score') or 0.0)   # 0..1
        penalty = min(max(risk, 0.0), 1.0) * ROUTE_RISK_PENALTY_MAX

        return {
            'health_score': round(max(0.0, engine_health - penalty), 2),
            'engine_health': engine_health,
            'route_risk_penalty': round(penalty, 2),
            'sensor_profile': profile,
        }

    def predict_lifetime(self, data: dict) -> float:
        """Remaining life in hours, proportional to the 0-100 health score."""
        return round(self.predict_health(data) / 100.0 * REMAINING_LIFE_MAX_HOURS, 1)

    # ── Routes / ports ───────────────────────────────────────────────────
    def recommend_routes(self, origin: str, destination: str,
                         ship_type: str = None, top_k: int = 3) -> list:
        """
        Find and recommend the best routes between two ports.

        Returns top_k routes ranked by weighted score (fuel + risk + time).
        """
        return self.optimizer.find_best_routes(
            origin=origin,
            destination=destination,
            ship_type=ship_type,
            top_k=top_k,
        )

    def get_ports(self) -> dict:
        """Return available origin and destination ports."""
        return self.optimizer.get_available_ports()