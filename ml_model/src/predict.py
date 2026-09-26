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


class MaritimePredictor:
    """Load trained models and make fuel/ETA predictions + route recommendations."""

    def __init__(self):
        self.fuel_model = None
        self.eta_model = None
        self.fuel_features = None
        self.eta_features = None
        self.optimizer = None
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

    def predict_health(self, data: dict) -> float:
        """Estimate engine health index from live sensor readings."""
        rpm_ratio = min(data.get('rpm', 80) / 120.0, 1.0)
        temp_ratio = max(0, 1 - (data.get('engineTemp', 75) - 60) / 60.0)
        vibration_ratio = max(0, 1 - data.get('vibration', 5) / 20.0)
        load_ratio = max(0, 1 - data.get('loadWeight', 1000) / 5000.0)

        health = (rpm_ratio * 0.3 + temp_ratio * 0.3 +
                  vibration_ratio * 0.25 + load_ratio * 0.15) * 100

        return round(float(health), 2)

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
    
    def predict_health(self, data):
        temp = data["engineTemp"]
        rpm = data["rpm"]
        vibration = data["vibration"]

        # simple logic (demo ML)
        health = 1.0
        if temp > 90:
          health -= 0.3
        if vibration > 3:
            health -= 0.3
        if rpm > 2000:
            health -= 0.2
        return max(0, health)
    def predict_lifetime(self, data):

        health = self.predict_health(data)
        # convert health → remaining life
        remaining_life = health * 200  # hours

        return remaining_life