"""Model wrapper for ship part lifetime prediction."""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

class ShipPartLifetimePredictor:
    def __init__(self, part_name: str, window_size: int = 30):
        self.part_name = part_name
        self.window_size = window_size
        self.model = None
        self.feature_columns = [
            'vibration', 'oil_pressure', 'exhaust_temp',
            'coolant_temp', 'rpm', 'oil_quality',
        ]

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # keep expected sensor columns; fill missing with median.
        for c in self.feature_columns:
            if c not in df.columns:
                df[c] = np.nan
        df = df[self.feature_columns]
        df = df.replace([np.inf, -np.inf], np.nan)
        if hasattr(self, 'training_medians'):
         df = df.fillna(self.training_medians)  # use training distribution
        else:
         df = df.fillna(df.median())            # fallback during training itself
        return df

    def train(self, part_df: pd.DataFrame) -> dict:
        if 'hour' not in part_df.columns:
            raise ValueError("Input data must contain 'hour' column")

        max_life = int(part_df['max_lifetime_hours'].iloc[0]) if 'max_lifetime_hours' in part_df.columns else 10000
        part_df = part_df.sort_values('hour')
        X = self._prepare_features(part_df)

        y = np.maximum(max_life - part_df['hour'], 0)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )

        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        self.model = model
        self.training_medians = X.median()
        self.sensor_stats = {
             col: {'q1': float(X[col].quantile(0.25)), 'q3': float(X[col].quantile(0.75))}
             for col in X.columns
            }
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        if r2 < 0:
              print(f"  [WARN] {self.part_name}: R²={r2:.4f} — model worse than a simple mean. Check your data.")
        metrics = {
            'part': self.part_name,
            'r2_score': float(r2),
            'accuracy_pct': float(max(0.0, min(100.0, r2 * 100.0))),
            'r2_raw': float(r2),
        }
        return metrics

    def predict(self, recent_sensor_df: pd.DataFrame, max_lifetime_hours: int) -> dict:
        if self.model is None:
            raise RuntimeError('Model not trained or loaded')

        X = self._prepare_features(recent_sensor_df)
        preds = self.model.predict(X)
        rul_hours = float(np.median(preds))
        health_score = float(np.clip((rul_hours / max_lifetime_hours) * 100.0, 0.0, 100.0))

        if health_score >= 75:
         alert = 'HEALTHY'
        elif health_score >= 50:
         alert = 'CAUTION'
        elif health_score >= 25:
         alert = 'WARNING'
        else:
         alert = 'CRITICAL'

        is_anomaly = False
        if hasattr(self, 'sensor_stats'):
          for col, stats in self.sensor_stats.items():
            if col in X.columns:
                iqr = stats['q3'] - stats['q1']
                if X[col].median() < stats['q1'] - 1.5 * iqr or X[col].median() > stats['q3'] + 1.5 * iqr:
                    is_anomaly = True
                    break

        return {
           'part_name': self.part_name,
           'health_score': round(health_score, 1),
           'rul_hours': round(rul_hours, 1),
           'rul_days': round(rul_hours / 24.0, 1),
           'alert_level': alert,
           'recommendation': 'Schedule inspection soon' if alert in ['CRITICAL', 'WARNING'] else 'Normal monitoring',
           'is_anomaly': is_anomaly,
       }

    def save(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        joblib.dump(self.model, os.path.join(folder, f"lifetime_{self.part_name.replace(' ', '_').lower()}.pkl"))
        joblib.dump(self.feature_columns, os.path.join(folder, f"lifetime_{self.part_name.replace(' ', '_').lower()}_cols.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str):
        inst = cls(part_name)
        inst.model = joblib.load(os.path.join(folder, f"lifetime_{part_name.replace(' ', '_').lower()}.pkl"))
        inst.feature_columns = joblib.load(os.path.join(folder, f"lifetime_{part_name.replace(' ', '_').lower()}_cols.pkl"))
        return inst
