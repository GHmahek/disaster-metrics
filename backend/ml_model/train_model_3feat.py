import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

BASE = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE, "..", "clean_flood_data.csv")
ART = os.path.join(BASE, "artifacts")


os.makedirs(ART, exist_ok=True)

# ---- Load dataset ----
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset missing at: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

FEATURES = ["MonsoonIntensity", "Urbanization", "DamsQuality"]
TARGET = "FloodProbability"

X = df[FEATURES]
y = df[TARGET]

# ---- Scale ----
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---- Train model ----
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_scaled, y)

# ---- Save artifacts ----
joblib.dump(model, os.path.join(ART, "flood_model_3feat.pkl"))
joblib.dump(scaler, os.path.join(ART, "scaler_3feat.pkl"))

print("\n🎉 Model training complete!")
print("Saved flood_model_3feat.pkl and scaler_3feat.pkl")
