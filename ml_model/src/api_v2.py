"""
FastAPI — Ship Part Lifetime Prediction (Separate Small Models)
================================================================
Run with:
    uvicorn api_v2:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /                                  Status + loaded models
    GET  /parts                             List all available parts

    GET  /prediction/health/{part_name}     Health score only
    GET  /prediction/rul/{part_name}        RUL only (hours + days)
    GET  /prediction/anomaly/{part_name}    Anomaly detection only
    GET  /prediction/alert/{part_name}      Alert level only
    GET  /prediction/all/{part_name}        All 4 combined

    POST /prediction/live/health            Live sensor → health score
    POST /prediction/live/rul               Live sensor → RUL
    POST /prediction/live/anomaly           Live sensor → anomaly flag
    POST /prediction/live/alert             Live sensor → alert level
    POST /prediction/live/all               Live sensor → all 4 combined
"""

import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))

from small_models import (
    HealthScoreModel,
    RULModel,
    AnomalyDetectorModel,
    AlertClassifier,
)

# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title="Ship Part Lifetime Prediction API v2",
    description="SIH1506 — Separate models for health, RUL, anomaly and alert prediction",
    version="2.0.0",
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
health_models:  dict = {}
rul_models:     dict = {}
anomaly_models: dict = {}
alert_models:   dict = {}
sensor_df: pd.DataFrame = None


# ── Schemas ───────────────────────────────────────────────
class SensorReading(BaseModel):
    part_name:    str   = Field(..., example="Tanker")
    vibration:    float = Field(..., ge=0.5,   le=10.0,  example=3.2)
    oil_pressure: float = Field(..., ge=1.0,   le=6.0,   example=2.8)
    exhaust_temp: float = Field(..., ge=200.0, le=600.0, example=420.0)
    coolant_temp: float = Field(..., ge=40.0,  le=130.0, example=78.0)
    rpm:          float = Field(..., ge=50.0,  le=150.0, example=100.0)
    oil_quality:  float = Field(..., ge=0.0,   le=1.0,   example=0.85)


class HealthResponse(BaseModel):
    part_name:    str
    health_score: float
    model:        str

class RULResponse(BaseModel):
    part_name: str
    rul_hours: float
    rul_days:  float
    model:     str

class AnomalyResponse(BaseModel):
    part_name:     str
    is_anomaly:    bool
    anomaly_score: float
    anomaly_votes: int
    window_size:   int
    model:         str

class AlertResponse(BaseModel):
    part_name:      str
    alert_level:    str
    recommendation: str
    confidence:     dict
    model:          str

class CombinedResponse(BaseModel):
    part_name:      str
    health_score:   float
    rul_hours:      float
    rul_days:       float
    is_anomaly:     bool
    anomaly_score:  float
    alert_level:    str
    recommendation: str
    confidence:     dict


# ── Startup ───────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    global health_models, rul_models, anomaly_models, alert_models, sensor_df

    path     = DATA_PATH
    fallback = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'new_maritime_dataset.csv')

    if not os.path.exists(path):
        if os.path.exists(fallback):
            path = fallback
        else:
            print("[ERROR] No dataset found.")
            return

    try:
        sensor_df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        sensor_df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')

    if 'part_name' not in sensor_df.columns:
        if 'ship_type' in sensor_df.columns:
            sensor_df['part_name'] = sensor_df['ship_type'].astype(str)

    if 'hour' not in sensor_df.columns:
        if 'voyage_hours' in sensor_df.columns:
            sensor_df['hour'] = pd.to_numeric(sensor_df['voyage_hours'], errors='coerce')
        else:
            sensor_df['hour'] = np.arange(len(sensor_df))

    sensor_df['hour'] = sensor_df['hour'].ffill().bfill().fillna(0)

    missing = [c for c in REQUIRED_SENSOR_COLS if c not in sensor_df.columns]
    if missing:
        rpm = pd.to_numeric(
            sensor_df.get('rpm', pd.Series(np.random.uniform(80, 130, len(sensor_df)))),
            errors='coerce'
        ).fillna(100)
        rpm = np.clip(rpm, 50, 150)
        np.random.seed(42)
        for col in missing:
            if col == 'vibration':
                sensor_df[col] = np.clip(2.0+(rpm/100)*2.0+np.random.normal(0,0.3,len(sensor_df)), 0.5, 8.0)
            elif col == 'oil_pressure':
                sensor_df[col] = np.clip(2.0+(rpm/100)*2.5+np.random.normal(0,0.2,len(sensor_df)), 1.0, 6.0)
            elif col == 'exhaust_temp':
                sensor_df[col] = np.clip(350+(rpm/100)*80+np.random.normal(0,10,len(sensor_df)), 300, 550)
            elif col == 'coolant_temp':
                sensor_df[col] = np.clip(75+(rpm/100)*10+np.random.normal(0,2,len(sensor_df)), 50, 120)
            elif col == 'oil_quality':
                sensor_df[col] = np.clip(0.95-(sensor_df['hour']/(sensor_df['hour'].max()+1))*0.3+np.random.normal(0,0.05,len(sensor_df)), 0, 1)

    sensor_df = sensor_df.sort_values(['part_name', 'hour']).reset_index(drop=True)

    # Train all 4 models per part
    for part_name in sensor_df['part_name'].dropna().unique():
        part_df  = sensor_df[sensor_df['part_name'] == part_name].copy()
        max_life = PART_LIFETIME_DEFAULTS.get(part_name, 10000)

        if len(part_df) < 50:
            continue

        print(f"\n[....] Training models for: {part_name}")

        try:
            m = HealthScoreModel(part_name)
            m.train(part_df, max_life)
            health_models[part_name] = {'model': m, 'max_life': max_life}
            print(f"  [OK] HealthScoreModel")
        except Exception as e:
            print(f"  [ERROR] HealthScoreModel: {e}")

        try:
            m = RULModel(part_name)
            m.train(part_df, max_life)
            rul_models[part_name] = {'model': m, 'max_life': max_life}
            print(f"  [OK] RULModel")
        except Exception as e:
            print(f"  [ERROR] RULModel: {e}")

        try:
            m = AnomalyDetectorModel(part_name)
            m.train(part_df)
            anomaly_models[part_name] = {'model': m, 'max_life': max_life}
            print(f"  [OK] AnomalyDetectorModel")
        except Exception as e:
            print(f"  [ERROR] AnomalyDetectorModel: {e}")

        try:
            m = AlertClassifier(part_name)
            m.train(part_df, max_life)
            alert_models[part_name] = {'model': m, 'max_life': max_life}
            print(f"  [OK] AlertClassifier")
        except Exception as e:
            print(f"  [ERROR] AlertClassifier: {e}")

    print(f"\n[OK] API ready")
    print(f"     Health models  : {len(health_models)}")
    print(f"     RUL models     : {len(rul_models)}")
    print(f"     Anomaly models : {len(anomaly_models)}")
    print(f"     Alert models   : {len(alert_models)}")


# ── Helper: build window from live reading ─────────────────
def build_live_window(reading: SensorReading) -> pd.DataFrame:
    row = {
        'vibration':    reading.vibration,
        'oil_pressure': reading.oil_pressure,
        'exhaust_temp': reading.exhaust_temp,
        'coolant_temp': reading.coolant_temp,
        'rpm':          reading.rpm,
        'oil_quality':  reading.oil_quality,
    }
    window         = pd.DataFrame([row] * 30)
    window['hour'] = range(30)
    return window


# Helper: get historical window
def get_historical_window(part_name: str, simulation_hour: int) -> pd.DataFrame:
    if sensor_df is None:
        raise HTTPException(status_code=503, detail="Data not loaded.")
    part_df = sensor_df[sensor_df['part_name'] == part_name]
    window  = part_df[part_df['hour'] <= simulation_hour].tail(30)
    if len(window) < 5:
        raise HTTPException(status_code=400, detail=f"Not enough data at hour {simulation_hour}.")
    return window


# ── Status ────────────────────────────────────────────────
@app.get("/", tags=["Status"])
def root():
    return {
        "status":         "running",
        "health_models":  len(health_models),
        "rul_models":     len(rul_models),
        "anomaly_models": len(anomaly_models),
        "alert_models":   len(alert_models),
        "parts":          list(health_models.keys()),
    }

@app.get("/parts", tags=["Status"])
def get_parts():
    return {"parts": list(health_models.keys())}


# ── Historical prediction endpoints ───────────────────────

@app.get("/prediction/health/{part_name}", response_model=HealthResponse, tags=["Historical"])
def predict_health(part_name: str, simulation_hour: int = 1500):
    """Health score for a part at a given simulation hour."""
    if part_name not in health_models:
        raise HTTPException(status_code=404, detail=f"No health model for '{part_name}'. Available: {list(health_models.keys())}")
    window = get_historical_window(part_name, simulation_hour)
    return health_models[part_name]['model'].predict(window)


@app.get("/prediction/rul/{part_name}", response_model=RULResponse, tags=["Historical"])
def predict_rul(part_name: str, simulation_hour: int = 1500):
    """Remaining Useful Life for a part at a given simulation hour."""
    if part_name not in rul_models:
        raise HTTPException(status_code=404, detail=f"No RUL model for '{part_name}'. Available: {list(rul_models.keys())}")
    window   = get_historical_window(part_name, simulation_hour)
    max_life = rul_models[part_name]['max_life']
    return rul_models[part_name]['model'].predict(window, max_life)


@app.get("/prediction/anomaly/{part_name}", response_model=AnomalyResponse, tags=["Historical"])
def predict_anomaly(part_name: str, simulation_hour: int = 1500):
    """Anomaly detection for a part at a given simulation hour."""
    if part_name not in anomaly_models:
        raise HTTPException(status_code=404, detail=f"No anomaly model for '{part_name}'. Available: {list(anomaly_models.keys())}")
    window = get_historical_window(part_name, simulation_hour)
    return anomaly_models[part_name]['model'].predict(window)


@app.get("/prediction/alert/{part_name}", response_model=AlertResponse, tags=["Historical"])
def predict_alert(part_name: str, simulation_hour: int = 1500):
    """Alert level for a part at a given simulation hour."""
    if part_name not in alert_models:
        raise HTTPException(status_code=404, detail=f"No alert model for '{part_name}'. Available: {list(alert_models.keys())}")
    window   = get_historical_window(part_name, simulation_hour)
    max_life = alert_models[part_name]['max_life']
    return alert_models[part_name]['model'].predict(window, max_life)


@app.get("/prediction/all/{part_name}", response_model=CombinedResponse, tags=["Historical"])
def predict_all(part_name: str, simulation_hour: int = 1500):
    """All 4 predictions combined for a part."""
    window = get_historical_window(part_name, simulation_hour)

    results = {}

    if part_name in health_models:
        results.update(health_models[part_name]['model'].predict(window))
    if part_name in rul_models:
        results.update(rul_models[part_name]['model'].predict(window, rul_models[part_name]['max_life']))
    if part_name in anomaly_models:
        results.update(anomaly_models[part_name]['model'].predict(window))
    if part_name in alert_models:
        results.update(alert_models[part_name]['model'].predict(window, alert_models[part_name]['max_life']))

    results['part_name'] = part_name
    return results


# ── Live sensor endpoints ─────────────────────────────────

@app.post("/prediction/live/health", response_model=HealthResponse, tags=["Live"])
def live_health(reading: SensorReading):
    """Submit live sensor readings → health score only."""
    if reading.part_name not in health_models:
        raise HTTPException(status_code=404, detail=f"No health model for '{reading.part_name}'.")
    return health_models[reading.part_name]['model'].predict(build_live_window(reading))


@app.post("/prediction/live/rul", response_model=RULResponse, tags=["Live"])
def live_rul(reading: SensorReading):
    """Submit live sensor readings → RUL only."""
    if reading.part_name not in rul_models:
        raise HTTPException(status_code=404, detail=f"No RUL model for '{reading.part_name}'.")
    max_life = rul_models[reading.part_name]['max_life']
    return rul_models[reading.part_name]['model'].predict(build_live_window(reading), max_life)


@app.post("/prediction/live/anomaly", response_model=AnomalyResponse, tags=["Live"])
def live_anomaly(reading: SensorReading):
    """Submit live sensor readings → anomaly detection only."""
    if reading.part_name not in anomaly_models:
        raise HTTPException(status_code=404, detail=f"No anomaly model for '{reading.part_name}'.")
    return anomaly_models[reading.part_name]['model'].predict(build_live_window(reading))


@app.post("/prediction/live/alert", response_model=AlertResponse, tags=["Live"])
def live_alert(reading: SensorReading):
    """Submit live sensor readings → alert level only."""
    if reading.part_name not in alert_models:
        raise HTTPException(status_code=404, detail=f"No alert model for '{reading.part_name}'.")
    max_life = alert_models[reading.part_name]['max_life']
    return alert_models[reading.part_name]['model'].predict(build_live_window(reading), max_life)


@app.post("/prediction/live/all", response_model=CombinedResponse, tags=["Live"])
def live_all(reading: SensorReading):
    """Submit live sensor readings → all 4 predictions combined."""
    part_name = reading.part_name
    window    = build_live_window(reading)
    results   = {}

    if part_name in health_models:
        results.update(health_models[part_name]['model'].predict(window))
    if part_name in rul_models:
        results.update(rul_models[part_name]['model'].predict(window, rul_models[part_name]['max_life']))
    if part_name in anomaly_models:
        results.update(anomaly_models[part_name]['model'].predict(window))
    if part_name in alert_models:
        results.update(alert_models[part_name]['model'].predict(window, alert_models[part_name]['max_life']))

    results['part_name'] = part_name
    return results