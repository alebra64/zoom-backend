from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ✅ CORRETTO endpoint globale
TOKEN_URL = "https://zoom.us/oauth/token"

@app.route('/')
def home():
    return jsonify({"message": "✅ Backend operativo. Usa /api/registrants?id=IDWEBINAR"})

@app.route('/api/registrants')
def get_registrants():
    webinar_id = request.args.get('id')
    if not webinar_id:
        return jsonify({"error": "ID webinar mancante"}), 400

    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    account_id = os.getenv("ZOOM_ACCOUNT_ID")

    if not all([client_id, client_secret, account_id]):
        return jsonify({"error": "Variabili d'ambiente mancanti"}), 500

    try:
        response = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "account_credentials",
                "account_id": account_id
            },
            auth=(client_id, client_secret)
        )
        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return jsonify({"error": "Access token non ottenuto", "zoom_response": token_data}), 400

        registrants_url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
        registrants_response = requests.get(
            registrants_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        data = registrants_response.json()

        if 'registrants' not in data:
            return jsonify({"error": "Nessun iscritto trovato o errore Zoom", "zoom_response": data}), 400

        simplified = [{
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "join_url": r["join_url"]
        } for r in data["registrants"]]

        return jsonify(simplified)

    except Exception as e:
        return jsonify({"error": f"Eccezione durante richiesta token: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
