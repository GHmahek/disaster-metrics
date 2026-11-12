# backend/graph_data.py

import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "clean_flood_data.csv")


def load_graph_dataset():
    """
    Loads the dataset and returns graph data for:
    - MonsoonIntensity vs FloodProbability
    - Urbanization vs FloodProbability
    - DamsQuality vs FloodProbability
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset missing at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # LIMIT DATA to avoid lag on charts
    MAX_POINTS = 700  
    df = df.head(MAX_POINTS)

    return {
        "monsoon": {
            "x": df["MonsoonIntensity"].tolist(),
            "y": df["FloodProbability"].tolist(),
        },
        "urban": {
            "x": df["Urbanization"].tolist(),
            "y": df["FloodProbability"].tolist(),
        },
        "dams": {
            "x": df["DamsQuality"].tolist(),
            "y": df["FloodProbability"].tolist(),
        }
    }
