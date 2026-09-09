from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


@app.post("/route")
def get_routes(data: RouteRequest):
    routes = predictor.recommend_routes(
        origin=data.origin,
        destination=data.destination,
        ship_type=data.ship_type,
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

    try:
        input_data = {
            "rpm": data.rpm,
            "engineTemp": data.engineTemp,
            "vibration": data.vibration,
            "loadWeight": data.loadWeight
        }

        health_score = float(predictor.predict_health(input_data))

        if health_score >= 80:
            alert = "HEALTHY"
        elif health_score >= 50:
            alert = "WARNING"
        else:
            alert = "CRITICAL"

        return {
            "health_score": health_score,
            "alert_level": alert
        }

    except Exception as e:
        return {"error": str(e)}

# 3. VOYAGE HEALTH

class RouteSelection(BaseModel):
    origin: str
    destination: str
    ship_type: str = None
    route_index: int = 0


@app.post("/voyage/health")
def voyage_health(data: RouteSelection):

    try:
        routes = predictor.recommend_routes(
            origin=data.origin,
            destination=data.destination,
            ship_type=data.ship_type,
            top_k=3
        )

        selected_route = routes[data.route_index]

        input_data = {
            "rpm": selected_route.get("rpm", 80),
            "engineTemp": selected_route.get("engine_temp", 75),
            "vibration": selected_route.get("vibration", 2),
            "loadWeight": selected_route.get("load", 1000)
        }

        health_score = float(predictor.predict_health(input_data))

        if health_score >= 80:
            alert = "HEALTHY"
        elif health_score >= 50:
            alert = "WARNING"
        else:
            alert = "CRITICAL"

        return {
            "selected_route": selected_route,
            "health_score": health_score,
            "alert_level": alert
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
    "AI-Agent (RAG + Langchain system) [Akhand]",
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
