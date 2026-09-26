import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import DATA_PATH

model = SentenceTransformer("all-MiniLM-L6-v2")
df = pd.read_csv(DATA_PATH)
numeric_columns = list(df.select_dtypes(include=["number"]).columns)
column_embeddings = model.encode([c.replace("_", " ") for c in numeric_columns])

# Check specific multi-word tokens first
PRIORITY_METRICS = [
    ("wind speed", "wind_speed_knots"),
    ("wave height", "wave_height_m"),
    ("engine load", "engine_load_pct"),
    ("engine temp", "engine_temp_c"),
    ("shaft power", "shaft_power_kw"),
    ("carbon emission", "co2_emitted_tonnes"),
    ("vessel speed", "avg_speed_knots"),
    ("ship speed", "avg_speed_knots"),
    ("cruising speed", "avg_speed_knots"),
    ("fuel consumption", "fuel_consumption_t_day"),
    ("fuel burn", "fuel_consumption_t_day"),
    ("wind", "wind_speed_knots"),
    ("wave", "wave_height_m"),
    ("speed", "avg_speed_knots"),
    ("fuel", "fuel_consumption_t_day"),
    ("load", "engine_load_pct"),
    ("rpm", "rpm")
]

def detect_metric(question: str) -> str:
    q = question.lower()
    for phrase, col in PRIORITY_METRICS:
        if phrase in q and col in numeric_columns:
            return col

    # Fallback to semantic similarity
    q_emb = model.encode([question])
    sims = cosine_similarity(q_emb, column_embeddings)[0]
    return numeric_columns[sims.argmax()]