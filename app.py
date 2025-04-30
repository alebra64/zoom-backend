from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')
ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID')

TOKEN_URL = "https://zoom.us/oauth/token"
REGISTRANTS_URL = "https://api.zoom.us/v2/webinars/{}/registrants"

def get_access_token():
    try:
        response = requests.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {requests.auth._basic_auth_str(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)}",
            },
            params={
                "grant_type": "account_credentials",
                "account_id": ZOOM_ACCOUNT_ID,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        return None

@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID del webinar mancante"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Access token non ottenuto"}), 400

    registrants = []
    next_page_token = ""

    try:
        while True:
            url = REGISTRANTS_URL.format(webinar_id)
            params = {"page_size": 30}
            if next_page_token:
                params["next_page_token"] = next_page_token

            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            r = requests.get(url, headers=headers, params=params)
            data = r.json()

            if "registrants" not in data:
                return jsonify({"error": "Errore nel recupero dei dati", "zoom_response": data}), 500

            for reg in data["registrants"]:
                registrants.append({
                    "first_name": reg.get("first_name", ""),
                    "last_name": reg.get("last_name", ""),
                    "email": reg.get("email", ""),
                    "join_url": reg.get("join_url", "")
                })

            next_page_token = data.get("next_page_token", "")
            if not next_page_token:
                break

        return jsonify(registrants)

    except Exception as e:
        return jsonify({"error": f"Eccezione: {str(e)}"}), 500

@app.route("/")
def home():
    return "✅ API Zoom attiva. Usa /api/registrants?id=IDWEBINAR"
