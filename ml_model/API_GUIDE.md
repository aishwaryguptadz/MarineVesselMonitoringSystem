# SyntheticAI — API Integration Guide (For Backend Developer)

## Overview

The ML models are trained and saved as `.pkl` files. Your job is to wrap them in a REST API (Flask / FastAPI) so the frontend can call them.

---

## Project Location & Structure

```
ml_model/
├── models/
│   ├── fuel_model.pkl           ← XGBoost fuel prediction model
│   ├── eta_model.pkl            ← Random Forest ETA model
│   ├── fuel_feature_cols.pkl    ← List of feature column names for fuel model
│   ├── eta_feature_cols.pkl     ← List of feature column names for ETA model
│   ├── label_encoders.pkl       ← Fitted label encoders for categorical columns
│   └── scaler.pkl               ← Fitted StandardScaler for numeric columns
├── src/
│   ├── predict.py               ← Ready-to-use MaritimePredictor class
│   └── route_optimizer.py       ← Route optimization engine
├── data/raw/
│   └── new_maritime_dataset.csv ← Training dataset
└── main.py                      ← CLI (for reference)
```

---

## Quick Start — Loading Models in Your API

```python
import joblib
import numpy as np

# Load models
fuel_model = joblib.load('models/fuel_model.pkl')
eta_model = joblib.load('models/eta_model.pkl')
fuel_features = joblib.load('models/fuel_feature_cols.pkl')
eta_features = joblib.load('models/eta_feature_cols.pkl')
```

---

## API Endpoints to Create

### 1. `POST /api/predict/fuel`

Predicts fuel consumption for a voyage.

**Request body:**
```json
{
  "dwt": 287185,
  "vessel_age": 21,
  "distance_nm": 8278,
  "avg_speed_knots": 12.0,
  "design_speed_knots": 16.0,
  "engine_load_pct": 42.6,
  "rpm": 91,
  "shaft_power_kw": 5743.3,
  "sfoc_g_kwh": 186.7,
  "wind_speed_knots": 1.8,
  "wave_height_m": 2.16,
  "current_speed_knots": 2.3,
  "hull_fouling_pct": 15.6,
  "propeller_fouling_pct": 14.1,
  "cargo_utilization_pct": 0.833,
  "draft_m": 13.68,
  "ship_type": "Tanker",
  "loading_condition": "Laden",
  "fuel_type": "VLSFO"
}
```

**Response:**
```json
{
  "predicted_fuel_tonnes": 739.6,
  "predicted_eta_hours": 689.8
}
```

### 2. `POST /api/routes/optimize`

Finds the best 3 routes between two ports.

**Request body:**
```json
{
  "origin": "Jebel Ali",
  "destination": "Guangzhou",
  "ship_type": "Tanker"
}
```

**Response:**
```json
{
  "routes": [
    {
      "rank": 1,
      "labels": ["Best Overall", "Most Fuel-Efficient"],
      "path": "Jebel Ali → Guangzhou",
      "route_type": "moderate",
      "total_fuel_t": 1123.0,
      "total_distance_nm": 5929,
      "voyage_days": 17.0,
      "fuel_cost_usd": 661750,
      "risk_score": 0.606,
      "overall_score": 0.18
    },
    ...
  ]
}
```

### 3. `GET /api/ports`

Returns available origin and destination ports.

---

## Using the Existing `predict.py` (Recommended)

The `MaritimePredictor` class in `src/predict.py` already handles model loading. Example FastAPI integration:

```python
from fastapi import FastAPI
import sys
sys.path.insert(0, 'src')
from predict import MaritimePredictor

app = FastAPI()
predictor = MaritimePredictor()  # loads models on startup

@app.post("/api/routes/optimize")
def optimize_route(origin: str, destination: str, ship_type: str = None):
    routes = predictor.recommend_routes(origin, destination, ship_type, top_k=3)
    return {"routes": routes}

@app.get("/api/ports")
def get_ports():
    return predictor.get_ports()
```

---

## Available Ports (Hardcoded in Dataset)

**Origins (11):** Bandar Abbas, Callao, Houston, Jebel Ali, Long Beach, New York, Port Klang, Santos, Tokyo, Vancouver, Yokohama

**Destinations (15):** Barcelona, Busan, Colon, Felixstowe, Genoa, Guangzhou, Hamburg, Hong Kong, Jakarta, Kaohsiung, Los Angeles, New York, Ningbo-Zhoushan, Piraeus, Tanjung Pelepas

---

## Dependencies

```
pip install pandas numpy scikit-learn xgboost joblib fastapi uvicorn
```

## Run API Server

```
uvicorn api:app --host 0.0.0.0 --port 8000
```
