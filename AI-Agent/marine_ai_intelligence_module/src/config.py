import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if running inside src/ or root
if os.path.basename(BASE_DIR) == "src":
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
else:
    PROJECT_ROOT = BASE_DIR

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "master_maritime_dataset.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "carbon_emission_model.pkl")
IMO_FILE = os.path.join(PROJECT_ROOT, "knowledge", "imo_regulations.txt")