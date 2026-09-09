from database import get_connection
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PATH SETUP ----------------
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))

ml_src = os.path.join(project_root, "ml_model", "src")
sys.path.append(ml_src)

from predict import MaritimePredictor

predictor = MaritimePredictor()

# ---------------- ROUTE API ----------------
@app.post("/route")
def get_routes(origin: str, destination: str, ship_type: str = None):
    routes = predictor.recommend_routes(
        origin=origin,
        destination=destination,
        ship_type=ship_type,
        top_k=3
    )
    return {"routes": routes}

@app.get("/ports")
def get_ports():
    return predictor.get_ports()

# ---------------- METRICS ----------------
@app.get("/vessel/metrics")
def get_vessel_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 10 engineTemp, rpm, fuelRate, speed,
               vibration, loadWeight, timestamp
        FROM vessel_metrics
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "engineTemp": r.engineTemp,
            "rpm": r.rpm,
            "fuelRate": r.fuelRate,
            "speed": r.speed,
            "vibration": r.vibration,
            "loadWeight": r.loadWeight,
            "timestamp": r.timestamp
        }
        for r in rows
    ]

# ---------------- FUEL PREDICTION ----------------
@app.get("/prediction/fuel")
def fuel_prediction():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 rpm, engineTemp, speed, loadWeight
        FROM vessel_metrics
        ORDER BY timestamp DESC
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"message": "No data found"}

    data = {
        "rpm": row.rpm,
        "engineTemp": row.engineTemp,
        "speed": row.speed,
        "loadWeight": row.loadWeight
    }

    result = predictor.predict_fuel(data)

    return {
        "input": data,
        "prediction": result
    }

# ---------------- SAFETY ----------------
@app.get("/prediction/safety")
def safety_prediction():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 riskScore, riskLevel, possibleCause
        FROM safety_predictions
        ORDER BY created_at DESC
    """)

    r = cursor.fetchone()
    conn.close()

    if r is None:
        return {"message": "No data"}

    return {
        "riskScore": r.riskScore,
        "riskLevel": r.riskLevel,
        "possibleCause": r.possibleCause
    }

# ---------------- HEALTH (YOUR MODEL) ----------------
@app.get("/prediction/health")
def get_health():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 engineTemp, rpm, vibration, loadWeight
        FROM vessel_metrics
        ORDER BY timestamp DESC
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"message": "No data"}

    data = {
        "engineTemp": row.engineTemp,
        "rpm": row.rpm,
        "vibration": row.vibration,
        "loadWeight": row.loadWeight
    }

    health_index = predictor.predict_health(data)

    return {
        "sensor_data": data,
        "health_index": float(health_index)
    }

# ---------------- ALERTS ----------------
@app.get("/alerts")
def get_alerts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT alert_id, severity, message, time
        FROM alerts
        ORDER BY time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "alertId": r.alert_id,
            "severity": r.severity,
            "message": r.message,
            "time": r.time
        }
        for r in rows
    ]

# ---------------- LOGS ----------------
@app.get("/logs")
def get_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT event, level, time
        FROM system_logs
        ORDER BY time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "event": r.event,
            "level": r.level,
            "time": r.time
        }
        for r in rows
    ]

# ---------------- STATUS ----------------
@app.get("/vessel/status")
def vessel_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT systemHealth, connectivity
        FROM system_status
    """)

    r = cursor.fetchone()
    conn.close()

    if r is None:
        return {"message": "No status"}

    return {
        "systemHealth": r.systemHealth,
        "connectivity": r.connectivity
    }

# ---------------- SETTINGS ----------------
class SettingsUpdate(BaseModel):
    refreshInterval: int
    aiMode: str
    apiEndpoint: str

@app.post("/settings/update")
def update_settings(data: SettingsUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO settings(refreshInterval, aiMode, apiEndpoint)
        VALUES (?, ?, ?)
    """, data.refreshInterval, data.aiMode, data.apiEndpoint)

    conn.commit()
    conn.close()

    return {"message": "Settings updated successfully"}

ai_path = os.path.join(project_root, "AI-Agent (RAG + Langchain system) [Akhand]","marine_ai_intelligence_module")
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
    if "sea" in question or "wave" in question:
        root_causes.append("Rough sea increases propulsion demand")
    if "engine" in question:
        root_causes.append("High engine load increases fuel usage")

    return {
        "question": data.question,
        "analysis": analysis,
        "root_causes": root_causes if root_causes else ["General system behavior"],
        "correlations": [
            "Fuel consumption ↔ Engine load",
            "Carbon emission ↔ Fuel consumption"
        ],
        "report": "AI-generated maritime insight based on dataset trends"
    }
