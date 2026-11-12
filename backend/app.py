
import os
import requests
import pandas as pd

from flask import Flask, request, jsonify
from flask_cors import CORS

from ml_model.predict import predict_risk


# --------------------------
# FLASK CONFIGURATION
# --------------------------

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "clean_flood_data.csv"
)

WEATHER_KEY_PATH = os.path.join(
    BASE_DIR,
    "weather",
    "api_key.txt"
)


# --------------------------
# 1. WEATHER API
# --------------------------

@app.route("/api/weather", methods=["GET"])
def api_weather():

    try:
        city = request.args.get("q", "Indore").strip()

        if not city:
            return jsonify({
                "error": "Please enter a city name"
            }), 400

        # Check API key file
        if not os.path.exists(WEATHER_KEY_PATH):
            return jsonify({
                "error": "Weather API key file not found"
            }), 500

        # Read API key
        with open(WEATHER_KEY_PATH, "r") as f:
            API_KEY = f.read().strip()

        if not API_KEY:
            return jsonify({
                "error": "Weather API key is empty"
            }), 500

        # OpenWeather API request
        url = "https://api.openweathermap.org/data/2.5/weather"

        response = requests.get(
            url,
            params={
                "q": city,
                "units": "metric",
                "appid": API_KEY
            },
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:
            return jsonify({
                "error": data.get(
                    "message",
                    "Unable to fetch weather data"
                )
            }), response.status_code

        return jsonify(data), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Weather API request timed out"
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# --------------------------
# 2. FLOOD PREDICTION API
# --------------------------

@app.route("/api/predict", methods=["POST"])
def api_predict():

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid prediction input"
            }), 400

        result = predict_risk({
            "monsoon": data.get("monsoon", 0),
            "urban": data.get("urban", 0),
            "dams": data.get("dams", 0)
        })

        return jsonify({
            "status": "ok",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# --------------------------
# 3. FLOOD GRAPH DATA API
# --------------------------

@app.route("/api/graphs", methods=["GET"])
def api_graphs():

    try:

        if not os.path.exists(DATA_PATH):
            return jsonify({
                "error": "Flood dataset not found"
            }), 500

        df = pd.read_csv(DATA_PATH)

        required_columns = [
            "MonsoonIntensity",
            "Urbanization",
            "DamsQuality",
            "FloodProbability"
        ]

        # Check required dataset columns
        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            return jsonify({
                "error": "Missing columns: " +
                ", ".join(missing_columns)
            }), 500

        # Prepare graph data
        output = {

            "monsoon": {
                "x": df["MonsoonIntensity"].tolist(),
                "y": df["FloodProbability"].tolist()
            },

            "urban": {
                "x": df["Urbanization"].tolist(),
                "y": df["FloodProbability"].tolist()
            },

            "dams": {
                "x": df["DamsQuality"].tolist(),
                "y": df["FloodProbability"].tolist()
            }

        }

        return jsonify(output), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# --------------------------
# 4. ROOT ROUTE
# --------------------------

@app.route("/")
def home():

    return jsonify({
        "status": "success",
        "message": "Disaster Metrics Backend Running"
    })


# --------------------------
# 5. RUN FLASK SERVER
# --------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
