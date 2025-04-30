from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")

def get_access_token():
    url = "https://zoom.us/oauth/token"
    headers = {"Authorization": f"Basic {requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)}"}
    payload = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

@app.route("/")
def home():
    return "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"

@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Access token non ottenuto"}), 500

    url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("registrants", [])
        result = [{
            "first_name": r.get("first_name"),
            "last_name": r.get("last_name"),
            "email": r.get("email"),
            "join_url": r.get("join_url")
        } for r in data]
        return jsonify(result)
    else:
        return jsonify({"error": f"Errore nella chiamata Zoom: {response.text}"}), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


