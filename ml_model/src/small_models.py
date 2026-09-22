"""
Small Specialized Models for Ship Part Lifetime Prediction
==========================================================
Four separate model classes, each doing one job:

    HealthScoreModel      → predicts health % (0-100)
    RULModel              → predicts remaining useful life in hours
    AnomalyDetectorModel  → flags abnormal sensor readings
    AlertClassifier       → classifies HEALTHY/CAUTION/WARNING/CRITICAL

Usage:
    from small_models import HealthScoreModel, RULModel, AnomalyDetectorModel, AlertClassifier

    # Train
    health_model   = HealthScoreModel(part_name="Tanker")
    rul_model      = RULModel(part_name="Tanker")
    anomaly_model  = AnomalyDetectorModel(part_name="Tanker")
    alert_model    = AlertClassifier(part_name="Tanker")

    health_model.train(part_df, max_lifetime_hours=10000)
    rul_model.train(part_df, max_lifetime_hours=10000)
    anomaly_model.train(part_df)
    alert_model.train(part_df, max_lifetime_hours=10000)

    # Predict
    result = health_model.predict(sensor_window)
    result = rul_model.predict(sensor_window, max_lifetime_hours=10000)
    result = anomaly_model.predict(sensor_window)
    result = alert_model.predict(sensor_window, max_lifetime_hours=10000)

    # Save / Load
    health_model.save("models")
    health_model = HealthScoreModel.load("Tanker", "models")
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
from sklearn.preprocessing import LabelEncoder


# ── Shared sensor columns ─────────────────────────────────
FEATURE_COLUMNS = [
    'vibration', 'oil_pressure', 'exhaust_temp',
    'coolant_temp', 'rpm', 'oil_quality',
]


# ── Shared feature preparation ────────────────────────────
def prepare_features(df: pd.DataFrame, training_medians=None) -> pd.DataFrame:
    """
    Keep only sensor columns, fill missing values.
    Uses training_medians at inference to avoid small-window bias.
    """
    df = df.copy()
    for c in FEATURE_COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[FEATURE_COLUMNS]
    df = df.replace([np.inf, -np.inf], np.nan)
    if training_medians is not None:
        df = df.fillna(training_medians)
    else:
        df = df.fillna(df.median())
    return df


# ─────────────────────────────────────────────────────────
# 1. HEALTH SCORE MODEL
# ─────────────────────────────────────────────────────────

class HealthScoreModel:
    """
    Predicts component health as a percentage (0–100%).
    100% = brand new, 0% = end of life.

    Target: health = (RUL / max_lifetime) * 100
    Algorithm: Random Forest Regressor
    """

    def __init__(self, part_name: str):
        self.part_name        = part_name
        self.model            = None
        self.training_medians = None

    def train(self, part_df: pd.DataFrame, max_lifetime_hours: int) -> dict:
        if 'hour' not in part_df.columns:
            raise ValueError("DataFrame must contain 'hour' column")

        part_df = part_df.sort_values('hour')
        X       = prepare_features(part_df)

        self.training_medians = X.median()

        # Target: health score 0-100
        rul    = np.maximum(max_lifetime_hours - part_df['hour'].values, 0)
        y      = np.clip((rul / max_lifetime_hours) * 100.0, 0, 100)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        r2     = r2_score(y_test, y_pred)

        if r2 < 0:
            print(f"  [WARN] {self.part_name} HealthScoreModel: R²={r2:.4f} — check data quality.")

        return {
            'part':      self.part_name,
            'model':     'HealthScoreModel',
            'r2_score':  round(float(r2), 4),
            'r2_raw':    round(float(r2), 4),
        }

    def predict(self, sensor_window: pd.DataFrame) -> dict:
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        X            = prepare_features(sensor_window, self.training_medians)
        predictions  = self.model.predict(X)
        health_score = float(np.clip(np.median(predictions), 0, 100))

        return {
            'part_name':    self.part_name,
            'health_score': round(health_score, 1),
            'model':        'HealthScoreModel',
        }

    def save(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        safe = self.part_name.replace(' ', '_').lower()
        joblib.dump({
            'model':            self.model,
            'training_medians': self.training_medians,
        }, os.path.join(folder, f"health_{safe}.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str):
        safe  = part_name.replace(' ', '_').lower()
        data  = joblib.load(os.path.join(folder, f"health_{safe}.pkl"))
        inst  = cls(part_name)
        inst.model            = data['model']
        inst.training_medians = data['training_medians']
        return inst


# ─────────────────────────────────────────────────────────
# 2. RUL MODEL
# ─────────────────────────────────────────────────────────

class RULModel:
    """
    Predicts Remaining Useful Life (RUL) in hours.

    Target: RUL = max_lifetime - current_hour
    Algorithm: Random Forest Regressor
    """

    def __init__(self, part_name: str):
        self.part_name        = part_name
        self.model            = None
        self.training_medians = None

    def train(self, part_df: pd.DataFrame, max_lifetime_hours: int) -> dict:
        if 'hour' not in part_df.columns:
            raise ValueError("DataFrame must contain 'hour' column")

        part_df = part_df.sort_values('hour')
        X       = prepare_features(part_df)

        self.training_medians = X.median()

        # Target: RUL in hours
        y = np.maximum(max_lifetime_hours - part_df['hour'].values, 0).astype(float)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        r2     = r2_score(y_test, y_pred)
        mae    = float(np.mean(np.abs(y_test - y_pred)))

        if r2 < 0:
            print(f"  [WARN] {self.part_name} RULModel: R²={r2:.4f} — check data quality.")

        return {
            'part':      self.part_name,
            'model':     'RULModel',
            'r2_score':  round(float(r2), 4),
            'r2_raw':    round(float(r2), 4),
            'mae_hours': round(mae, 1),
        }

    def predict(self, sensor_window: pd.DataFrame, max_lifetime_hours: int) -> dict:
        # Fallback: if only 1 alert class existed in training data,
        # derive alert level from health score using simple thresholds
        if self.model is None:
            rul          = max(max_lifetime_hours - int(sensor_window["hour"].median()) if "hour" in sensor_window.columns else max_lifetime_hours, 0)
            health_score = min((rul / max_lifetime_hours) * 100, 100)
            alert_level  = (
                "HEALTHY"  if health_score >= 75 else
                "CAUTION"  if health_score >= 50 else
                "WARNING"  if health_score >= 25 else
                "CRITICAL"
            )
            recommendation = (
                "Immediate maintenance required" if alert_level == "CRITICAL" else
                "Schedule inspection soon"        if alert_level == "WARNING"  else
                "Monitor closely"                 if alert_level == "CAUTION"  else
                "Normal monitoring"
            )
            return {
                "part_name":      self.part_name,
                "alert_level":    alert_level,
                "recommendation": recommendation,
                "confidence":     {alert_level: 1.0},
                "model":          "AlertClassifier (threshold fallback)",
            }

        X         = prepare_features(sensor_window, self.training_medians)
        preds     = self.model.predict(X)
        rul_hours = float(np.clip(np.median(preds), 0, max_lifetime_hours))

        return {
            'part_name': self.part_name,
            'rul_hours': round(rul_hours, 1),
            'rul_days':  round(rul_hours / 24.0, 1),
            'model':     'RULModel',
        }

    def save(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        safe = self.part_name.replace(' ', '_').lower()
        joblib.dump({
            'model':            self.model,
            'training_medians': self.training_medians,
        }, os.path.join(folder, f"rul_{safe}.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str):
        safe  = part_name.replace(' ', '_').lower()
        data  = joblib.load(os.path.join(folder, f"rul_{safe}.pkl"))
        inst  = cls(part_name)
        inst.model            = data['model']
        inst.training_medians = data['training_medians']
        return inst


# ─────────────────────────────────────────────────────────
# 3. ANOMALY DETECTOR MODEL
# ─────────────────────────────────────────────────────────

class AnomalyDetectorModel:
    """
    Detects abnormal sensor readings using Isolation Forest.

    Unlike the IQR method in the original model, Isolation Forest
    learns the normal pattern from training data and flags anything
    that deviates from it — even subtle multi-sensor anomalies.

    Returns: is_anomaly (bool) + anomaly_score (float, lower = more abnormal)
    """

    def __init__(self, part_name: str, contamination: float = 0.05):
        """
        Args:
            contamination: Expected proportion of anomalies in training data.
                           0.05 means ~5% of readings are expected to be anomalous.
        """
        self.part_name        = part_name
        self.contamination    = contamination
        self.model            = None
        self.training_medians = None

    def train(self, part_df: pd.DataFrame) -> dict:
        X = prepare_features(part_df)
        self.training_medians = X.median()
        X = prepare_features(part_df, self.training_medians)

        self.model = IsolationForest(
            n_estimators  = 100,
            contamination = self.contamination,
            random_state  = 42,
            n_jobs        = -1,
        )
        self.model.fit(X)

        # Self-evaluation: how many training points flagged as anomaly
        labels         = self.model.predict(X)
        anomaly_count  = int(np.sum(labels == -1))
        anomaly_rate   = round(anomaly_count / len(X) * 100, 1)

        return {
            'part':          self.part_name,
            'model':         'AnomalyDetectorModel',
            'anomaly_rate':  anomaly_rate,
            'total_samples': len(X),
        }

    def predict(self, sensor_window: pd.DataFrame) -> dict:
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        X      = prepare_features(sensor_window, self.training_medians)
        labels = self.model.predict(X)           # 1 = normal, -1 = anomaly
        scores = self.model.score_samples(X)     # lower = more anomalous

        # If majority of the window rows are flagged → anomaly
        anomaly_votes = int(np.sum(labels == -1))
        is_anomaly    = anomaly_votes > len(labels) * 0.4   # >40% of window flagged
        avg_score     = float(np.mean(scores))

        return {
            'part_name':     self.part_name,
            'is_anomaly':    is_anomaly,
            'anomaly_score': round(avg_score, 4),   # lower = more abnormal
            'anomaly_votes': anomaly_votes,
            'window_size':   len(labels),
            'model':         'AnomalyDetectorModel',
        }

    def save(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        safe = self.part_name.replace(' ', '_').lower()
        joblib.dump({
            'model':            self.model,
            'training_medians': self.training_medians,
            'contamination':    self.contamination,
        }, os.path.join(folder, f"anomaly_{safe}.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str):
        safe  = part_name.replace(' ', '_').lower()
        data  = joblib.load(os.path.join(folder, f"anomaly_{safe}.pkl"))
        inst  = cls(part_name, contamination=data['contamination'])
        inst.model            = data['model']
        inst.training_medians = data['training_medians']
        return inst


# ─────────────────────────────────────────────────────────
# 4. ALERT CLASSIFIER MODEL
# ─────────────────────────────────────────────────────────

class AlertClassifier:
    """
    Classifies component status into alert levels:
        HEALTHY  → health >= 75%
        CAUTION  → health 50–74%
        WARNING  → health 25–49%
        CRITICAL → health < 25%

    Unlike a simple threshold check, this learns the relationship
    between sensor patterns and alert levels directly from data,
    so it can catch edge cases the thresholds miss.

    Algorithm: Random Forest Classifier
    """

    ALERT_LEVELS = ['HEALTHY', 'CAUTION', 'WARNING', 'CRITICAL']

    def __init__(self, part_name: str):
        self.part_name        = part_name
        self.model            = None
        self.training_medians = None
        self.label_encoder    = LabelEncoder()

    def _make_labels(self, part_df: pd.DataFrame, max_lifetime_hours: int) -> np.ndarray:
        """Convert hours → health % → alert label."""
        rul          = np.maximum(max_lifetime_hours - part_df['hour'].values, 0)
        health_score = np.clip((rul / max_lifetime_hours) * 100, 0, 100)

        labels = np.where(
            health_score >= 75, 'HEALTHY',
            np.where(
                health_score >= 50, 'CAUTION',
                np.where(health_score >= 25, 'WARNING', 'CRITICAL')
            )
        )
        return labels

    def train(self, part_df: pd.DataFrame, max_lifetime_hours: int) -> dict:
        if 'hour' not in part_df.columns:
            raise ValueError("DataFrame must contain 'hour' column")

        part_df = part_df.sort_values('hour')
        X       = prepare_features(part_df)

        self.training_medians = X.median()

        y_str = self._make_labels(part_df, max_lifetime_hours)
        y     = self.label_encoder.fit_transform(y_str)

        # Check we have at least 2 classes — skip if only 1 level in data
        if len(np.unique(y)) < 2:
            print(f"  [WARN] {self.part_name} AlertClassifier: only 1 alert class in data — skipping.")
            return {'part': self.part_name, 'model': 'AlertClassifier', 'accuracy': 0.0}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)

        y_pred   = self.model.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))

        # Class distribution
        unique, counts = np.unique(y_str, return_counts=True)
        distribution   = dict(zip(unique.tolist(), counts.tolist()))

        return {
            'part':         self.part_name,
            'model':        'AlertClassifier',
            'accuracy':     round(accuracy * 100, 1),
            'distribution': distribution,
        }

    def predict(self, sensor_window: pd.DataFrame, max_lifetime_hours: int) -> dict:
        # Fallback: if only 1 alert class existed in training data,
        # derive alert level from health score using simple thresholds
        if self.model is None:
            rul          = max(max_lifetime_hours - int(sensor_window["hour"].median()) if "hour" in sensor_window.columns else max_lifetime_hours, 0)
            health_score = min((rul / max_lifetime_hours) * 100, 100)
            alert_level  = (
                "HEALTHY"  if health_score >= 75 else
                "CAUTION"  if health_score >= 50 else
                "WARNING"  if health_score >= 25 else
                "CRITICAL"
            )
            recommendation = (
                "Immediate maintenance required" if alert_level == "CRITICAL" else
                "Schedule inspection soon"        if alert_level == "WARNING"  else
                "Monitor closely"                 if alert_level == "CAUTION"  else
                "Normal monitoring"
            )
            return {
                "part_name":      self.part_name,
                "alert_level":    alert_level,
                "recommendation": recommendation,
                "confidence":     {alert_level: 1.0},
                "model":          "AlertClassifier (threshold fallback)",
            }

        X          = prepare_features(sensor_window, self.training_medians)
        y_encoded  = self.model.predict(X)
        y_labels   = self.label_encoder.inverse_transform(y_encoded)

        # Most frequent alert in the window
        unique, counts = np.unique(y_labels, return_counts=True)
        alert_level    = unique[np.argmax(counts)]

        # Probability of each class for the median row
        proba      = self.model.predict_proba(X)
        avg_proba  = np.mean(proba, axis=0)
        classes    = self.label_encoder.inverse_transform(self.model.classes_)
        confidence = dict(zip(classes.tolist(), np.round(avg_proba, 3).tolist()))

        recommendation = (
            'Immediate maintenance required'   if alert_level == 'CRITICAL' else
            'Schedule inspection soon'         if alert_level == 'WARNING'  else
            'Monitor closely'                  if alert_level == 'CAUTION'  else
            'Normal monitoring'
        )

        return {
            'part_name':      self.part_name,
            'alert_level':    alert_level,
            'recommendation': recommendation,
            'confidence':     confidence,   # e.g. {"HEALTHY": 0.82, "CAUTION": 0.12, ...}
            'model':          'AlertClassifier',
        }

    def save(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        safe = self.part_name.replace(' ', '_').lower()
        joblib.dump({
            'model':            self.model,
            'training_medians': self.training_medians,
            'label_encoder':    self.label_encoder,
        }, os.path.join(folder, f"alert_{safe}.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str):
        safe  = part_name.replace(' ', '_').lower()
        data  = joblib.load(os.path.join(folder, f"alert_{safe}.pkl"))
        inst  = cls(part_name)
        inst.model            = data['model']
        inst.training_medians = data['training_medians']
        inst.label_encoder    = data['label_encoder']
        return inst