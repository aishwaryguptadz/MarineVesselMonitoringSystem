import joblib
from .config import MODEL_PATH

# Load model once when module starts
try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None


def predict_carbon(fuel, engine, speed):

    if model is None:
        return {"error": "Carbon prediction model could not be loaded"}

    try:
        fuel = float(fuel)
        engine = float(engine)
        speed = float(speed)

        prediction = model.predict([[fuel, engine, speed]])[0]

        emission = round(float(prediction), 3)

        # Simple emission classification
        if emission < 20:
            level = "Low"
        elif emission < 30:
            level = "Moderate"
        else:
            level = "High"

        return {
            "predicted_carbon_emission": emission,
            "units": "tons CO2",
            "emission_level": level
        }

    except ValueError:
        return {"error": "Invalid numeric input"}