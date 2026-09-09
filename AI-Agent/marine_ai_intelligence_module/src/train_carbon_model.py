import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
from .config import DATA_PATH, MODEL_PATH

df = pd.read_csv(DATA_PATH)

X = df[["fuel_consumption_t_day","engine_load_pct","avg_speed_knots"]]
y = df["co2_emitted_tonnes"]

model = LinearRegression()

model.fit(X,y)

joblib.dump(model,MODEL_PATH)

print("Carbon model trained")