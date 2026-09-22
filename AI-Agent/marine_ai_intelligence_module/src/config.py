import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "master_maritime_dataset.csv")

MODEL_PATH = os.path.join(BASE_DIR, "models", "carbon_emission_model.pkl")

IMO_FILE = os.path.join(BASE_DIR, "knowledge", "imo_regulations.txt")