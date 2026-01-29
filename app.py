import os
import requests
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DB_URL = os.getenv("FIREBASE_DB_URL")
DB_SECRET = os.getenv("FIREBASE_DB_SECRET")

if not DB_URL or not DB_SECRET:
    raise Exception("Firebase environment variables not set")

LAST_SAVE_TIME = 0
SAVE_INTERVAL = 300

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/riwayat')
def riwayat():
    logs = []
    try:
        endpoint = f"{DB_URL}/history_logs.json"
        params = {
            "auth": DB_SECRET,
            "orderBy": "\"$key\"",
            "limitToLast": 50
        }

        response = requests.get(endpoint, params=params)
        data_riwayat = response.json()

        if data_riwayat:
            for key in reversed(list(data_riwayat.keys())):
                item = data_riwayat[key]
                logs.append({
                    "timestamp": item.get("timestamp", "-"),
                    "pm2_5": item.get("pm2_5", 0),
                    "pm10": item.get("gas_mq135", 0),
                    "temperature": item.get("temperature", 0),
                    "humidity": item.get("humidity", 0)
                })

    except Exception as e:
        print(f"Error riwayat: {e}")
        logs = []

    return render_template("riwayat.html", logs=logs)

@app.route('/pengaturan')
def pengaturan():
    return render_template("pengaturan.html")

@app.route('/api/home')
def get_live_data():
    global LAST_SAVE_TIME

    try:
        endpoint = f"{DB_URL}/AirQuality.json"
        params = {"auth": DB_SECRET}
        response = requests.get(endpoint, params=params)
        raw_data = response.json()

        if not raw_data:
            return jsonify({
                "pm2_5": 0,
                "pm10": 0,
                "temperature": 0,
                "humidity": 0
            })

        clean_data = {
            "pm2_5": round(float(raw_data.get("dust", 0)), 2),
            "pm10": int(raw_data.get("gas_mq135", 0)),
            "temperature": raw_data.get("temperature", 0),
            "humidity": raw_data.get("humidity", 0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        current_time = time.time()
        if current_time - LAST_SAVE_TIME > SAVE_INTERVAL:
            save_to_history(clean_data)
            LAST_SAVE_TIME = current_time

        return jsonify(clean_data)

    except Exception as e:
        print(f"Error API: {e}")
        return jsonify({"error": str(e)}), 500

def save_to_history(data):
    try:
        endpoint = f"{DB_URL}/history_logs.json"
        params = {"auth": DB_SECRET}

        payload = {
            "timestamp": data["timestamp"],
            "pm2_5": data["pm2_5"],
            "gas_mq135": data["pm10"],
            "temperature": data["temperature"],
            "humidity": data["humidity"]
        }

        requests.post(endpoint, params=params, json=payload)

    except Exception as e:
        print(f"Gagal menyimpan history: {e}")

@app.route('/api/save_settings', methods=['POST'])
def save_settings_api():
    return jsonify({"status": "success"}), 200
