import os
import json
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Home Assistant interne API-Daten
HA_URL = "http://supervisor/core/api"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
IS_MOCK_MODE = HA_TOKEN is None  # Wenn kein Token vorhanden ist, im Mock-Modus laufen

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "content-type": "application/json",
}

if IS_MOCK_MODE:
    print("\n" + "="*50)
    print("MOCK-MODUS AKTIV: Befehle werden nur simuliert!")
    print("="*50 + "\n")

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    # Serviert die index.html aus dem 'templates'-Ordner
    return render_template("index.html")

@app.route("/api/devices", methods=["GET"])
def get_config():
    try:
        return jsonify(load_config())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/control", methods=["POST"])
def control_device():
    data = request.json
    entity_id = data.get("entity_id")
    action = data.get("action")

    config = load_config()
    allowed_ids = [item["id"] for item in config["erlaubte_entitaeten"]]

    # Test, ob Zugriff auf das Gerät erlaubt ist
    if entity_id not in allowed_ids:
        return jsonify({"status": "error", "message": "Zugriff Verweigert!"}), 403
    
    #domain bestimmen (Licht oder Rolladen)
    domain = entity_id.split(".")[0]

    if IS_MOCK_MODE:
        print(f"[MOCK-API] Befehl empfangen: {domain}.{action} für {entity_id}")
        return jsonify({"status": "success", "mode": "mock"})

    # Befehl an Home Assistant Core weiterleiten
    ha_endpoint = f"{HA_URL}/services/{domain}/{action}"
    payload = {"entity_id": entity_id}

    try:
        response = requests.post(ha_endpoint, headers=HEADERS, json=payload, timeout=5)
        if response.status_code in [200,201]:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Home Assistant API Fehler"}), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) 