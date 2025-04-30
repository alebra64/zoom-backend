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
REGISTRANTS_URL_TEMPLATE = "https://api.zoom.us/v2/webinars/{webinar_id}/registrants"

def get_access_token():
    try:
        response = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            params={
                "grant_type": "account_credentials",
                "account_id": ACCOUNT_ID
            },
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        return None

@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Access token non ottenuto"}), 400

    registrants = []
    next_page_token = ""

    while True:
        url = f"{REGISTRANTS_URL_TEMPLATE.format(webinar_id=webinar_id)}?page_size=30"
        if next_page_token:
            url += f"&next_page_token={next_page_token}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            return jsonify({
                "error": "Errore nella richiesta Zoom",
                "status": response.status_code,
                "zoom_response": response.text
            }), response.status_code

        data = response.json()
        registrants += data.get("registrants", [])
        next_page_token = data.get("next_page_token", "")
        if not next_page_token:
            break

    cleaned = [
        {
            "first_name": r.get("first_name"),
            "last_name": r.get("last_name"),
            "email": r.get("email"),
            "join_url": r.get("join_url")
        }
        for r in registrants
    ]
    return jsonify(cleaned)

@app.route("/")
def home():
    return jsonify({"message": "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
