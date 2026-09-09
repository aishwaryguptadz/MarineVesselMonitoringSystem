"""
LSTM-based ship part lifetime predictor.
Add this class to model.py alongside ShipPartLifetimePredictor.

Requirements:
    pip install tensorflow
"""

import os
import numpy as np
import pandas as pd
import joblib

# TensorFlow import with graceful fallback
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("[WARN] TensorFlow not installed. LSTMPredictor will not work.")
    print("       Install with: pip install tensorflow")


class ShipPartLSTMPredictor:
    """
    LSTM-based predictor for ship part Remaining Useful Life.

    Differences from ShipPartLifetimePredictor (Random Forest):
    - Treats the sensor window as a TIME SEQUENCE, not just statistics.
    - Learns how sensors change over time, not just their current values.
    - Generally more accurate when sensor degradation is gradual and sequential.

    Usage mirrors ShipPartLifetimePredictor exactly:
        predictor = ShipPartLSTMPredictor(part_name="Tanker")
        metrics   = predictor.train(part_df)
        pred      = predictor.predict(window_df, max_lifetime_hours)
        predictor.save("models")
    """

    FEATURE_COLUMNS = [
        'vibration', 'oil_pressure', 'exhaust_temp',
        'coolant_temp', 'rpm', 'oil_quality',
    ]

    def __init__(self, part_name: str, window_size: int = 30):
        if not TENSORFLOW_AVAILABLE:
            raise RuntimeError("TensorFlow is required. Run: pip install tensorflow")

        self.part_name    = part_name
        self.window_size  = window_size
        self.model        = None
        self.feature_cols = self.FEATURE_COLUMNS
        self.n_features   = len(self.feature_cols)

        # Normalisation stats — saved during training, used at inference
        self.x_mean: np.ndarray = None
        self.x_std:  np.ndarray = None
        self.y_mean: float      = None
        self.y_std:  float      = None

        # Anomaly detection — IQR stats per sensor
        self.sensor_stats: dict = {}

    # ──────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────

    def _build_model(self) -> Sequential:
        """Build the LSTM architecture."""
        model = Sequential([
            Input(shape=(self.window_size, self.n_features)),

            # First LSTM layer — returns sequences so next LSTM can read them
            LSTM(64, return_sequences=True),
            Dropout(0.2),

            # Second LSTM layer — returns single vector
            LSTM(32, return_sequences=False),
            Dropout(0.2),

            # Output: single RUL value
            Dense(16, activation='relu'),
            Dense(1),
        ])
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae'],
        )
        return model

    def _normalise_X(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """Z-score normalise features. fit=True during training to save stats."""
        if fit:
            self.x_mean = X.mean(axis=(0, 1))   # mean per feature across all windows and timesteps
            self.x_std  = X.std(axis=(0, 1)) + 1e-8
        return (X - self.x_mean) / self.x_std

    def _normalise_y(self, y: np.ndarray, fit: bool = False) -> np.ndarray:
        if fit:
            self.y_mean = float(y.mean())
            self.y_std  = float(y.std()) + 1e-8
        return (y - self.y_mean) / self.y_std

    def _denormalise_y(self, y_norm: np.ndarray) -> np.ndarray:
        return y_norm * self.y_std + self.y_mean

    def _make_windows(
        self,
        df: pd.DataFrame,
        max_life: float,
    ):
        """
        Slide a window of size `window_size` over the sorted sensor data.

        Returns:
            X : (n_samples, window_size, n_features)
            y : (n_samples,)  — RUL in hours at the END of each window
        """
        # Fill missing sensor columns
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df[self.feature_cols + ['hour']].copy()
        df = df.replace([np.inf, -np.inf], np.nan).fillna(df.median())

        sensor_vals = df[self.feature_cols].values   # (T, n_features)
        hours       = df['hour'].values               # (T,)

        X_list, y_list = [], []
        for i in range(len(df) - self.window_size):
            window = sensor_vals[i : i + self.window_size]          # (W, F)
            rul    = max(max_life - hours[i + self.window_size], 0)  # scalar
            X_list.append(window)
            y_list.append(rul)

        if not X_list:
            return np.empty((0, self.window_size, self.n_features)), np.empty(0)

        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.float32)

    # ──────────────────────────────────────────────────────
    # Training
    # ──────────────────────────────────────────────────────

    def train(self, part_df: pd.DataFrame, epochs: int = 50, batch_size: int = 32) -> dict:
        """
        Train the LSTM on historical sensor data.

        Args:
            part_df    : DataFrame for ONE part, must contain 'hour' column.
            epochs     : Max training epochs (early stopping may end sooner).
            batch_size : Mini-batch size.

        Returns:
            Metrics dict with r2_score, accuracy_pct, mae.
        """
        if 'hour' not in part_df.columns:
            raise ValueError("Input data must contain 'hour' column")

        max_life = (
            int(part_df['max_lifetime_hours'].iloc[0])
            if 'max_lifetime_hours' in part_df.columns
            else 10000
        )

        part_df = part_df.sort_values('hour').reset_index(drop=True)

        X, y = self._make_windows(part_df, max_life)
        if len(X) < 10:
            raise ValueError(f"Not enough windows to train ({len(X)} windows). Need at least 10.")

        # Save IQR anomaly stats from raw (un-normalised) sensor data
        raw_sensors = part_df[[c for c in self.feature_cols if c in part_df.columns]]
        self.sensor_stats = {
            col: {
                'q1': float(raw_sensors[col].quantile(0.25)),
                'q3': float(raw_sensors[col].quantile(0.75)),
            }
            for col in raw_sensors.columns
        }

        # Train/test split (80/20, no shuffle — preserve time order)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Normalise
        X_train = self._normalise_X(X_train, fit=True)
        X_test  = self._normalise_X(X_test,  fit=False)
        y_train = self._normalise_y(y_train,  fit=True)
        y_test_norm = self._normalise_y(y_test, fit=False)

        # Build and train
        self.model = self._build_model()

        callbacks = [
            EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-5),
        ]

        self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test_norm),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=0,
        )

        # Evaluate
        y_pred_norm = self.model.predict(X_test, verbose=0).flatten()
        y_pred      = self._denormalise_y(y_pred_norm)

        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - y_test.mean()) ** 2)
        r2     = float(1 - ss_res / (ss_tot + 1e-8))
        mae    = float(np.mean(np.abs(y_test - y_pred)))

        if r2 < 0:
            print(f"  [WARN] {self.part_name} LSTM: R²={r2:.4f} — model worse than mean. Check data.")

        return {
            'part':         self.part_name,
            'model_type':   'LSTM',
            'r2_score':     r2,
            'r2_raw':       r2,
            'accuracy_pct': float(max(0.0, min(100.0, r2 * 100.0))),
            'mae_hours':    mae,
        }

    # ──────────────────────────────────────────────────────
    # Inference
    # ──────────────────────────────────────────────────────

    def predict(self, recent_sensor_df: pd.DataFrame, max_lifetime_hours: int) -> dict:
        """
        Predict RUL from a recent sensor window.

        Args:
            recent_sensor_df  : Last N rows of sensor data (N >= window_size ideally).
            max_lifetime_hours: Maximum lifetime for this part.

        Returns:
            Prediction dict (same structure as ShipPartLifetimePredictor).
        """
        if self.model is None:
            raise RuntimeError("Model not trained or loaded.")
        if self.x_mean is None:
            raise RuntimeError("Normalisation stats missing — retrain the model.")

        df = recent_sensor_df.copy()
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df[self.feature_cols].replace([np.inf, -np.inf], np.nan).fillna(df.median())

        # Pad or trim to exactly window_size rows
        vals = df.values.astype(np.float32)
        if len(vals) < self.window_size:
            pad  = np.tile(vals[0], (self.window_size - len(vals), 1))
            vals = np.vstack([pad, vals])
        else:
            vals = vals[-self.window_size:]

        X = vals.reshape(1, self.window_size, self.n_features)
        X = (X - self.x_mean) / self.x_std   # normalise

        y_norm    = self.model.predict(X, verbose=0).flatten()[0]
        rul_hours = float(np.clip(self._denormalise_y(np.array([y_norm]))[0], 0, max_lifetime_hours))
        health_score = float(np.clip((rul_hours / max_lifetime_hours) * 100.0, 0.0, 100.0))

        # Alert level
        if health_score >= 75:
            alert = 'HEALTHY'
        elif health_score >= 50:
            alert = 'CAUTION'
        elif health_score >= 25:
            alert = 'WARNING'
        else:
            alert = 'CRITICAL'

        # Anomaly detection (IQR on current window)
        is_anomaly = False
        if self.sensor_stats:
            for col, stats in self.sensor_stats.items():
                col_idx = self.feature_cols.index(col) if col in self.feature_cols else None
                if col_idx is not None:
                    col_vals = vals[:, col_idx]
                    iqr      = stats['q3'] - stats['q1']
                    lower    = stats['q1'] - 1.5 * iqr
                    upper    = stats['q3'] + 1.5 * iqr
                    if float(np.median(col_vals)) < lower or float(np.median(col_vals)) > upper:
                        is_anomaly = True
                        break

        return {
            'part_name':      self.part_name,
            'health_score':   round(health_score, 1),
            'rul_hours':      round(rul_hours, 1),
            'rul_days':       round(rul_hours / 24.0, 1),
            'alert_level':    alert,
            'recommendation': 'Schedule inspection soon' if alert in ['CRITICAL', 'WARNING'] else 'Normal monitoring',
            'is_anomaly':     is_anomaly,
            'model_type':     'LSTM',
        }

    # ──────────────────────────────────────────────────────
    # Persistence
    # ──────────────────────────────────────────────────────

    def save(self, folder: str):
        """Save Keras model + normalisation stats to folder."""
        os.makedirs(folder, exist_ok=True)
        safe = self.part_name.replace(' ', '_').lower()

        # Save Keras model
        self.model.save(os.path.join(folder, f"lstm_{safe}.keras"))

        # Save stats
        joblib.dump({
            'x_mean':       self.x_mean,
            'x_std':        self.x_std,
            'y_mean':       self.y_mean,
            'y_std':        self.y_std,
            'sensor_stats': self.sensor_stats,
            'feature_cols': self.feature_cols,
            'window_size':  self.window_size,
        }, os.path.join(folder, f"lstm_{safe}_stats.pkl"))

    @classmethod
    def load(cls, part_name: str, folder: str) -> 'ShipPartLSTMPredictor':
        """Load a previously saved LSTM predictor."""
        safe = part_name.replace(' ', '_').lower()
        inst = cls(part_name)

        inst.model = load_model(os.path.join(folder, f"lstm_{safe}.keras"))

        stats = joblib.load(os.path.join(folder, f"lstm_{safe}_stats.pkl"))
        inst.x_mean       = stats['x_mean']
        inst.x_std        = stats['x_std']
        inst.y_mean       = stats['y_mean']
        inst.y_std        = stats['y_std']
        inst.sensor_stats = stats['sensor_stats']
        inst.feature_cols = stats['feature_cols']
        inst.window_size  = stats['window_size']
        inst.n_features   = len(inst.feature_cols)

        return inst