import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN_URL = "https://zoom-eu.zoom.us/oauth/token"
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")

def get_access_token():
    try:
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
            return f"Errore token Zoom: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Eccezione durante richiesta token: {str(e)}"

@app.route("/api/registrants")
def get_registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    access_token = get_access_token()
    if isinstance(access_token, str) and access_token.startswith("Errore"):
        return jsonify({"error": access_token}), 500
    elif isinstance(access_token, str) and access_token.startswith("Eccezione"):
        return jsonify({"error": access_token}), 500

    try:
        url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            registrants = response.json().get("registrants", [])
            result = [{
                "first_name": r.get("first_name"),
                "last_name": r.get("last_name"),
                "email": r.get("email"),
                "join_url": r.get("join_url")
            } for r in registrants]
            return jsonify(result)
        else:
            return jsonify({
                "error": f"Errore dati registrants: {response.status_code}",
                "zoom_response": response.text
            }), response.status_code
    except Exception as e:
        return jsonify({"error": f"Eccezione durante richiesta registrants: {str(e)}"}), 500

@app.route("/")
def home():
    return jsonify({"message": "✅ API funzionante. Usa /api/registrants?id=IDWEBINAR"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
