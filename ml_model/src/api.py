"""
FastAPI wrapper for Ship Part Lifetime Prediction System
=========================================================
Run with:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /                          Health check
    GET  /prediction/health         Get predictions for all parts
    GET  /prediction/{part_name}    Get prediction for a specific part
    POST /prediction/live           Submit manual sensor readings
"""

import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# ── Path setup ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from model import ShipPartLifetimePredictor

# ── App setup ─────────────────────────────────────────────
app = FastAPI(
    title="Ship Part Lifetime Prediction API",
    description="SIH1506 — Predicts remaining useful life of ship components",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_maritime_dataset.csv')

PART_LIFETIME_DEFAULTS = {
    "Main Engine Bearing": 12000,
    "Turbocharger":        10000,
    "Fuel Pump":            9000,
    "Gearbox":             11000,
    "Cooling System":       9500,
    "Exhaust Valve":        8000,
    "Bulk Carrier":        10000,
    "Container Ship":      10000,
    "Gas Carrier":         10000,
    "General Cargo":       10000,
    "Tanker":              10000,
}

REQUIRED_SENSOR_COLS = [
    'vibration', 'oil_pressure', 'exhaust_temp',
    'coolant_temp', 'rpm', 'oil_quality',
]

# ── Global state ──────────────────────────────────────────
trained_models: dict = {}
sensor_df: pd.DataFrame = None


# ── Pydantic schemas ──────────────────────────────────────
class SensorReading(BaseModel):
    part_name: str = Field(..., example="Main Engine Bearing")
    vibration: float = Field(..., ge=0.5, le=10.0,  example=3.2)
    oil_pressure: float = Field(..., ge=1.0, le=6.0,   example=2.8)
    exhaust_temp: float = Field(..., ge=200.0, le=600.0, example=420.0)
    coolant_temp: float = Field(..., ge=40.0, le=130.0, example=78.0)
    rpm: float = Field(..., ge=50.0, le=150.0, example=100.0)
    oil_quality: float = Field(..., ge=0.0, le=1.0,   example=0.85)


class PredictionResult(BaseModel):
    part_name: str
    health_score: float
    rul_hours: float
    rul_days: float
    alert_level: str
    recommendation: str
    is_anomaly: bool


# ── Startup — load data and train models ──────────────────
@app.on_event("startup")
async def startup_event():
    global trained_models, sensor_df

    # Load data
    path = DATA_PATH
    fallback = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'new_maritime_dataset.csv')

    if not os.path.exists(path):
        if os.path.exists(fallback):
            path = fallback
        else:
            print("[ERROR] No dataset found — predictions will not work until data is available.")
            return

    try:
        sensor_df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        sensor_df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')

    # Column normalisation
    if 'part_name' not in sensor_df.columns:
        if 'ship_type' in sensor_df.columns:
            sensor_df['part_name'] = sensor_df['ship_type'].astype(str)

    if 'hour' not in sensor_df.columns:
        if 'voyage_hours' in sensor_df.columns:
            sensor_df['hour'] = pd.to_numeric(sensor_df['voyage_hours'], errors='coerce')
        else:
            sensor_df['hour'] = np.arange(len(sensor_df))

    sensor_df['hour'] = sensor_df['hour'].ffill().bfill().fillna(0)

    # Generate synthetic sensor cols if missing
    missing = [c for c in REQUIRED_SENSOR_COLS if c not in sensor_df.columns]
    if missing:
        rpm = pd.to_numeric(sensor_df.get('rpm', pd.Series(np.random.uniform(80, 130, len(sensor_df)))), errors='coerce').fillna(100)
        rpm = np.clip(rpm, 50, 150)
        np.random.seed(42)
        for col in missing:
            if col == 'vibration':
                sensor_df[col] = np.clip(2.0 + (rpm / 100.0) * 2.0 + np.random.normal(0, 0.3, len(sensor_df)), 0.5, 8.0)
            elif col == 'oil_pressure':
                sensor_df[col] = np.clip(2.0 + (rpm / 100.0) * 2.5 + np.random.normal(0, 0.2, len(sensor_df)), 1.0, 6.0)
            elif col == 'exhaust_temp':
                sensor_df[col] = np.clip(350.0 + (rpm / 100.0) * 80.0 + np.random.normal(0, 10, len(sensor_df)), 300.0, 550.0)
            elif col == 'coolant_temp':
                sensor_df[col] = np.clip(75.0 + (rpm / 100.0) * 10.0 + np.random.normal(0, 2, len(sensor_df)), 50.0, 120.0)
            elif col == 'oil_quality':
                sensor_df[col] = np.clip(0.95 - (sensor_df['hour'] / (sensor_df['hour'].max() + 1)) * 0.3 + np.random.normal(0, 0.05, len(sensor_df)), 0.0, 1.0)

    sensor_df = sensor_df.sort_values(['part_name', 'hour']).reset_index(drop=True)

    # Train one model per part
    for part_name in sensor_df['part_name'].dropna().unique():
        part_df = sensor_df[sensor_df['part_name'] == part_name].copy()
        if len(part_df) < 50:
            continue
        try:
            predictor = ShipPartLifetimePredictor(part_name=part_name, window_size=30)
            predictor.train(part_df)
            trained_models[part_name] = {
                'predictor': predictor,
                'max_lifetime_hours': PART_LIFETIME_DEFAULTS.get(part_name, 10000),
            }
            print(f"[OK] Trained model for: {part_name}")
        except Exception as e:
            print(f"[ERROR] Failed to train {part_name}: {e}")

    print(f"\n[OK] API ready — {len(trained_models)} models loaded.")


# ── Routes ────────────────────────────────────────────────

@app.get("/", tags=["Status"])
def root():
    return {
        "status": "running",
        "models_loaded": len(trained_models),
        "parts": list(trained_models.keys()),
    }


@app.get("/prediction/health", response_model=list[PredictionResult], tags=["Predictions"])
def get_all_predictions(simulation_hour: int = 1500):
    """Get lifetime predictions for all trained parts at a given simulation hour."""
    if not trained_models:
        raise HTTPException(status_code=503, detail="No models loaded. Check dataset path.")

    results = []
    for part_name, info in trained_models.items():
        part_df = sensor_df[sensor_df['part_name'] == part_name]
        window = part_df[part_df['hour'] <= simulation_hour].tail(30)
        if len(window) < 5:
            continue
        try:
            pred = info['predictor'].predict(window, info['max_lifetime_hours'])
            results.append(pred)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed for {part_name}: {str(e)}")

    if not results:
        raise HTTPException(status_code=404, detail="No predictions could be generated.")

    return results


@app.get("/prediction/{part_name}", response_model=PredictionResult, tags=["Predictions"])
def get_part_prediction(part_name: str, simulation_hour: int = 1500):
    """Get lifetime prediction for a single part."""
    if part_name not in trained_models:
        available = list(trained_models.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Part '{part_name}' not found. Available: {available}"
        )

    info = trained_models[part_name]
    part_df = sensor_df[sensor_df['part_name'] == part_name]
    window = part_df[part_df['hour'] <= simulation_hour].tail(30)

    if len(window) < 5:
        raise HTTPException(status_code=400, detail=f"Not enough data for '{part_name}' at hour {simulation_hour}.")

    try:
        pred = info['predictor'].predict(window, info['max_lifetime_hours'])
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prediction/live", response_model=PredictionResult, tags=["Predictions"])
def live_prediction(reading: SensorReading):
    """Submit live sensor readings and get an instant prediction."""
    part_name = reading.part_name

    if part_name not in trained_models:
        available = list(trained_models.keys())
        raise HTTPException(
            status_code=404,
            detail=f"No model for '{part_name}'. Available: {available}"
        )

    # Build a 30-row window from the single reading
    row = {
        'vibration':    reading.vibration,
        'oil_pressure': reading.oil_pressure,
        'exhaust_temp': reading.exhaust_temp,
        'coolant_temp': reading.coolant_temp,
        'rpm':          reading.rpm,
        'oil_quality':  reading.oil_quality,
    }
    window = pd.DataFrame([row] * 30)
    window['hour'] = range(30)

    info = trained_models[part_name]
    try:
        pred = info['predictor'].predict(window, info['max_lifetime_hours'])
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))