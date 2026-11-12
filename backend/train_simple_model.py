# backend/train_simple_model.py

import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

print("\n🚀 Training Simple Flood Model (3 Features)...")

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "clean_flood_data.csv")
ARTIFACT_DIR = os.path.join(BASE_DIR, "ml_model", "artifacts")

os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)
print("Dataset Loaded:", df.shape)

# Select only the required 3 input features
FEATURES = ["MonsoonIntensity", "Urbanization", "DamsQuality"]
TARGET = "FloodProbability"

df = df[FEATURES + [TARGET]]

X = df[FEATURES]
y = df[TARGET]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = RandomForestRegressor(n_estimators=300, random_state=42)
model.fit(X_scaled, y)

# Evaluate
preds = model.predict(X_scaled)
mse = mean_squared_error(y, preds)
print(f"MSE: {mse}")

# Save artifacts
joblib.dump(model, os.path.join(ARTIFACT_DIR, "simple_flood_model.pkl"))
joblib.dump(scaler, os.path.join(ARTIFACT_DIR, "simple_scaler.pkl"))
joblib.dump(FEATURES, os.path.join(ARTIFACT_DIR, "simple_features.pkl"))

print("\n🎉 Model saved successfully!")
print("Artifacts saved in:", ARTIFACT_DIR)
