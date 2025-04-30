from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
TOKEN_URL = "https://zoom.us/oauth/token"

def get_access_token():
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

@app.route("/api/registrants")
def registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Access token non ottenuto"}), 500

    url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        registrants = response.json().get("registrants", [])
        output = []
        for r in registrants:
            output.append({
                "first_name": r.get("first_name", ""),
                "last_name": r.get("last_name", ""),
                "email": r.get("email", ""),
                "join_url": r.get("join_url", "")
            })
        return jsonify(output)
    else:
        return jsonify({"error": "Errore nel recupero registranti"}), response.status_code

@app.route("/")
def home():
    return jsonify({"message": "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"})

# 🔥 Parte fondamentale per Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

