import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

print("\n🚀 Training 3-Feature Flood Model...\n")

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "clean_flood_data.csv")
ARTIFACT_DIR = os.path.join(BASE_DIR, "ml_model", "artifacts")

os.makedirs(ARTIFACT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# ------- USE ONLY 3 FEATURES --------
FEATURES = ["MonsoonIntensity", "Urbanization", "DamsQuality"]
TARGET = "FloodProbability"

X = df[FEATURES]
y = df[TARGET]

# ------- SCALING -------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ------- MODEL -------
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_scaled, y)

preds = model.predict(X_scaled)
mse = mean_squared_error(y, preds)

print("✔ Training done! MSE:", mse)

# ------- SAVE -------
joblib.dump(model, os.path.join(ARTIFACT_DIR, "flood_model_regressor.pkl"))
joblib.dump(scaler, os.path.join(ARTIFACT_DIR, "scaler.pkl"))

print("\n🎉 Saved model + scaler successfully!")

