import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Endpoint token Zoom
TOKEN_URL = "https://zoom-eu.zoom.us/oauth/token"  # Cambia se non usi EU endpoint

# ✅ Leggi le variabili dall'environment
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")

# ✅ Funzione per ottenere token
def get_access_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(
        TOKEN_URL,
        headers=headers,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data=data
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# ✅ Endpoint principale
@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Access token non ottenuto"}), 400

    url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        registrants = response.json().get("registrants", [])
        result = []
        for r in registrants:
            result.append({
                "first_name": r.get("first_name"),
                "last_name": r.get("last_name"),
                "email": r.get("email"),
                "join_url": r.get("join_url")
            })
        return jsonify(result)
    else:
        return jsonify({
            "error": "Errore nel recupero dei dati",
            "status": response.status_code,
            "zoom_response": response.text
        }), response.status_code

@app.route("/")
def home():
    return jsonify({"message": "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"})

# ✅ Per il run su Render
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
