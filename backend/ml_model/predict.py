import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(BASE_DIR, "artifacts")

MODEL_PATH = os.path.join(ART, "flood_model_3feat.pkl")
SCALER_PATH = os.path.join(ART, "scaler_3feat.pkl")

# Load trained model + scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def predict_risk(features):
    X = np.array([[features["monsoon"], features["urban"], features["dams"]]])
    X_scaled = scaler.transform(X)
    prob = float(model.predict(X_scaled)[0])

    if prob < 0.4:
        risk = "Low"
    elif prob < 0.7:
        risk = "Moderate"
    else:
        risk = "High"

    return {
        "probability": prob,
        "risk_level": risk
    }
