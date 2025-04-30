from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")

TOKEN_URL = "https://zoom.us/oauth/token"
REGISTRANTS_URL_TEMPLATE = "https://api.zoom.us/v2/webinars/{}/registrants?page_size=100&page_number={}"

def get_access_token():
    try:
        response = requests.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)}"
            },
            data={"grant_type": "account_credentials", "account_id": ACCOUNT_ID},
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
    page = 1
    while True:
        url = REGISTRANTS_URL_TEMPLATE.format(webinar_id, page)
        res = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
        if res.status_code != 200:
            return jsonify({
                "error": "Errore nel recupero iscritti Zoom",
                "status": res.status_code,
                "zoom_response": res.text
            }), res.status_code
        data = res.json()
        registrants += data.get("registrants", [])
        if not data.get("next_page_token"):
            break
        page += 1

    cleaned = [
        {
            "first_name": r.get("first_name", ""),
            "last_name": r.get("last_name", ""),
            "email": r.get("email", ""),
            "join_url": r.get("join_url", "")
        } for r in registrants
    ]
    return jsonify(cleaned)

@app.route("/")
def home():
    return jsonify({"message": "✅ Backend operativo. Usa /api/registrants?id=IDWEBINAR"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
