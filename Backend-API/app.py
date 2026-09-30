from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import sys

# ---------------- PATH SETUP ----------------
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))

ml_src = os.path.join(project_root, "ml_model", "src")
sys.path.append(ml_src)

# ---------------- IMPORT ML ----------------
from predict import MaritimePredictor
from feature_engineering import create_derived_features

# ---------------- INIT ----------------
predictor = MaritimePredictor()

# ---------------- HELPER FUNCTION ----------------
def prepare_features(input_dict):
    df = pd.DataFrame([input_dict])

    # Derived features
    df = create_derived_features(df)

    # Ensure all required features exist
    for col in predictor.fuel_features:
        if col not in df.columns:
            df[col] = 0

    return df

# ---------------- FASTAPI INIT ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. ROUTE API

class RouteRequest(BaseModel):
    origin: str
    destination: str
    ship_type: str = None
    shipType: Optional[str] = None      # the Android app sends camelCase


@app.post("/route")
def get_routes(data: RouteRequest):
    routes = predictor.recommend_routes(
        origin=data.origin,
        destination=data.destination,
        ship_type=data.ship_type or data.shipType,
        top_k=3
    )
    return {"routes": routes}

#  2. HEALTH API

class HealthInput(BaseModel):
    rpm: float
    engineTemp: float
    vibration: float
    loadWeight: float


@app.post("/prediction/health")
def get_health(data: HealthInput):
    """Health from explicit sensor readings. Score is 0-100."""
    try:
        health_score = predictor.predict_health(data.dict())

        return {
            "health_score": health_score,
            "alert_level": predictor.alert_level(health_score)
        }

    except Exception as e:
        return {"error": str(e)}

# 3. VOYAGE HEALTH

class RouteSelection(BaseModel):
    origin: str
    destination: str
    ship_type: str = None
    route_index: int = 0
    vessel_id: Optional[str] = None   # optional: score one specific vessel
    shipType: Optional[str] = None    # the Android app sends camelCase
    routeIndex: Optional[int] = None


@app.post("/voyage/health")
def voyage_health(data: RouteSelection):
    """
    Health for the chosen ship type on the chosen route.
    The score is computed from that ship type's real sensor data in the
    dataset (rpm, temperatures, load, turbo efficiency, fouling) and is reduced
    slightly for risky routes, so different ships/routes give different results.
    """
    try:
        # accept both snake_case (docs/tests) and camelCase (Android app)
        ship_type = data.ship_type or data.shipType
        route_index = data.routeIndex if data.routeIndex is not None else data.route_index

        routes = predictor.recommend_routes(
            origin=data.origin,
            destination=data.destination,
            ship_type=ship_type,
            top_k=3
        )

        if not routes:
            return {"error": f"No routes found from {data.origin} to {data.destination}."}
        if not 0 <= route_index < len(routes):
            return {"error": f"route_index must be between 0 and {len(routes) - 1}."}

        selected_route = routes[route_index]

        result = predictor.predict_voyage_health(
            ship_type=ship_type,
            route=selected_route,
            vessel_id=data.vessel_id
        )

        return {
            "selected_route": selected_route,
            "health_score": result["health_score"],
            "alert_level": predictor.alert_level(result["health_score"]),
            # extra detail (the Android app ignores unknown fields)
            "engine_health": result["engine_health"],
            "route_risk_penalty": result["route_risk_penalty"],
            "sensor_profile": result["sensor_profile"]
        }

    except Exception as e:
        return {"error": str(e)}

# 4. LIFETIME API

@app.post("/prediction/lifetime")
def get_lifetime(data: HealthInput):
    try:
        input_data = data.dict()
        lifetime = predictor.predict_lifetime(input_data)
        return {"remaining_life_hours": lifetime}
    except Exception as e:
        return {"error": str(e)}


#  5. CHATBOT API

ai_path = os.path.join(
    project_root,
    "AI-Agent",
    "marine_ai_intelligence_module"
)
sys.path.append(ai_path)

from src.query_engine import analyze_dataset

class Query(BaseModel):
    question: str


@app.post("/ask")
def ask_question(data: Query):
    analysis = analyze_dataset()
    question = data.question.lower()

    root_causes = []

    if "fuel" in question:
        root_causes.append("Fuel consumption depends on engine load and speed")
    if "sea" in question:
        root_causes.append("Rough sea increases propulsion demand")
    if "engine" in question:
        root_causes.append("High engine load increases fuel usage")

    return {
        "question": data.question,
        "analysis": analysis,
        "root_causes": root_causes if root_causes else ["General system behavior"],
        "report": "AI-generated maritime insight"
    }
