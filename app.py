from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# URL del token Zoom (per EU)
TOKEN_URL = "https://zoom-eu.zoom.us/oauth/token"

# Ottiene un token valido da Zoom
def get_access_token():
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    account_id = os.getenv("ZOOM_ACCOUNT_ID")

    if not all([client_id, client_secret, account_id]):
        return None, {"error": "Variabili ambiente mancanti"}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = (client_id, client_secret)
    data = {
        "grant_type": "account_credentials",
        "account_id": account_id
    }

    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data, auth=auth)
        if response.status_code == 200:
            return response.json()["access_token"], None
        else:
            return None, {
                "error": "Access token non ottenuto",
                "status": response.status_code,
                "zoom_response": response.text
            }
    except Exception as e:
        return None, {"error": str(e)}

# Route principale
@app.route("/")
def home():
    return "✅ API di iscritti attiva. Usa /api/registrants?id=ID_WEBINAR"

# Endpoint per ottenere iscritti
@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    token, error = get_access_token()
    if error:
        return jsonify(error), 400

    url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Errore nel recupero iscritti", "zoom_response": data}), response.status_code

        registrants = [
            {
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "email": r["email"],
                "join_url": r.get("join_url", "Non disponibile")
            }
            for r in data.get("registrants", [])
        ]
        return jsonify(registrants)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esecuzione del server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
