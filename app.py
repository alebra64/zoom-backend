import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
TOKEN_URL = "https://zoom.us/oauth/token"
REGISTRANTS_URL = "https://api.zoom.us/v2/webinars/{webinar_id}/registrants"

def get_access_token():
    try:
        response = requests.post(
            TOKEN_URL,
            params={"grant_type": "account_credentials", "account_id": ACCOUNT_ID},
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        return None

@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID del webinar mancante."}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Access token non ottenuto"}), 500

    headers = {"Authorization": f"Bearer {token}"}
    registrants = []
    next_page_token = ""

    while True:
        params = {"page_size": 30}
        if next_page_token:
            params["next_page_token"] = next_page_token

        response = requests.get(
            REGISTRANTS_URL.format(webinar_id=webinar_id),
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            return jsonify({"error": "Errore durante la richiesta Zoom", "status": response.status_code}), 500

        data = response.json()
        registrants.extend([
            {
                "email": r.get("email"),
                "first_name": r.get("first_name"),
                "last_name": r.get("last_name"),
                "join_url": r.get("join_url")
            } for r in data.get("registrants", [])
        ])

        next_page_token = data.get("next_page_token", "")
        if not next_page_token:
            break

    return jsonify(registrants)

@app.route("/")
def home():
    return jsonify({"message": "✅ Backend Zoom operativo. Usa /api/registrants?id=IDWEBINAR"})
