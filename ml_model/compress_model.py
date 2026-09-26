import joblib
import os

MODEL_PATH = "models/eta_model.pkl"

print("Loading original model...")

model = joblib.load(MODEL_PATH)

print("Saving compressed model...")

joblib.dump(model, MODEL_PATH, compress=9)

print("Compression complete!")

size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
print(f"New model size: {size:.2f} MB")