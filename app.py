import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Carica le variabili da environment se presenti
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "✅ Backend Zoom operativo. Usa /api/registrants?id=IDWEBINAR"})

@app.route('/api/registrants')
def get_registrants():
    webinar_id = request.args.get('id')

    if not webinar_id:
        return jsonify({"error": "ID del webinar mancante"}), 400

    account_id = os.getenv("ZOOM_ACCOUNT_ID")
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")

    if not all([account_id, client_id, client_secret]):
        return jsonify({"error": "Variabili di ambiente mancanti"}), 500

    # Ottieni access token
    token_url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(client_id, client_secret)}"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": account_id
    }

    try:
        token_response = requests.post(token_url, headers=headers, data=data)
        if token_response.status_code != 200:
            return jsonify({"error": "Access token non ottenuto", "status": token_response.status_code, "zoom_response": token_response.text}), 500

        access_token = token_response.json().get("access_token")

        # Ottieni gli iscritti al webinar
        registrants_url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
        registrants_headers = {
            "Authorization": f"Bearer {access_token}"
        }

        registrants_response = requests.get(registrants_url, headers=registrants_headers)

        if registrants_response.status_code != 200:
            return jsonify({"error": "Impossibile recuperare gli iscritti", "status": registrants_response.status_code, "zoom_response": registrants_response.text}), 500

        registrants = registrants_response.json().get("registrants", [])

        # Estraggo i dati richiesti
        output = [{
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "join_url": r.get("join_url", "")
        } for r in registrants]

        return jsonify(output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
