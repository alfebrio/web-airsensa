import requests
import json
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ==========================================
# 1. KONFIGURASI FIREBASE
# ==========================================
DB_URL = 'https://cat-feeder2-default-rtdb.firebaseio.com'
DB_SECRET = 'lmisPjzdMuBR1lQgmJBL4zBQvtCbz7btjBGJ7uMa'

# Konfigurasi Auto-Save
LAST_SAVE_TIME = 0
SAVE_INTERVAL = 300  # Simpan riwayat setiap 300 detik (5 menit) agar database tidak penuh

# ==========================================
# 2. ROUTE HALAMAN
# ==========================================

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/riwayat')
def riwayat():
    logs = []
    try:
        # Ambil data dari node 'history_logs'
        endpoint = f"{DB_URL}/history_logs.json"
        params = {
            'auth': DB_SECRET,
            'orderBy': '"$key"',
            'limitToLast': 50 # Ambil 50 data terakhir saja
        }
        
        response = requests.get(endpoint, params=params)
        data_riwayat = response.json()
        
        if data_riwayat:
            # Loop data dan format agar rapi di HTML
            for key in reversed(list(data_riwayat.keys())):
                item = data_riwayat[key]
                
                # Pastikan field ada, jika tidak kasih strip (-)
                logs.append({
                    'timestamp': item.get('timestamp', '-'),
                    'pm2_5': item.get('pm2_5', 0),
                    'pm10': item.get('gas_mq135', 0), # Mapping Gas ke PM10 field
                    'temperature': item.get('temperature', 0),
                    'humidity': item.get('humidity', 0)
                })
                
    except Exception as e:
        print(f"Error riwayat: {e}")
        logs = []

    return render_template('riwayat.html', logs=logs)

@app.route('/pengaturan')
def pengaturan():
    return render_template('pengaturan.html')

# ==========================================
# 3. ROUTE API & LOGIKA AUTO-SAVE
# ==========================================

@app.route('/api/home')
def get_live_data():
    global LAST_SAVE_TIME
    
    try:
        # 1. Ambil Data Live dari 'AirQuality'
        endpoint = f"{DB_URL}/AirQuality.json"
        params = {'auth': DB_SECRET}
        response = requests.get(endpoint, params=params)
        raw_data = response.json()
        
        if not raw_data:
            return jsonify({"pm2_5": 0, "pm10": 0, "temperature": 0, "humidity": 0})

        # Format Data
        clean_data = {
            "pm2_5": round(float(raw_data.get('dust', 0)), 2), 
            "pm10": int(raw_data.get('gas_mq135', 0)), 
            "temperature": raw_data.get('temperature', 0),
            "humidity": raw_data.get('humidity', 0),
            # Tambahkan timestamp saat ini
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        }

        # 2. LOGIKA AUTO-SAVE KE RIWAYAT
        # Cek apakah sudah waktunya menyimpan (setiap 5 menit)
        current_time = time.time()
        if current_time - LAST_SAVE_TIME > SAVE_INTERVAL:
            save_to_history(clean_data)
            LAST_SAVE_TIME = current_time
            print("LOG: Data otomatis tersimpan ke riwayat.")

        return jsonify(clean_data)

    except Exception as e:
        print(f"Error API: {e}")
        return jsonify({"error": str(e)}), 500

def save_to_history(data):
    """Fungsi pembantu untuk push data ke node history_logs"""
    try:
        endpoint = f"{DB_URL}/history_logs.json"
        params = {'auth': DB_SECRET}
        
        # Kita simpan field aslinya agar konsisten
        payload = {
            'timestamp': data['timestamp'],
            'pm2_5': data['pm2_5'],
            'gas_mq135': data['pm10'],
            'temperature': data['temperature'],
            'humidity': data['humidity']
        }
        
        # Method POST akan membuat key unik (push)
        requests.post(endpoint, params=params, json=payload)
    except Exception as e:
        print(f"Gagal menyimpan history: {e}")

@app.route('/api/save_settings', methods=['POST'])
def save_settings_api():
    # ... (Sama seperti sebelumnya) ...
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)