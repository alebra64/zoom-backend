from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dati di autenticazione Zoom
ACCOUNT_ID = "RmQMdjj1RtSpp97PrCJWZw"
CLIENT_ID = "JtzbddhBQjuo59Yrql03kA"
CLIENT_SECRET = "KIgp4N7vqlf85nUQkaSerZZ2pnKAvbUT"

# Ottieni un token valido da Zoom
def get_access_token():
    url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)}"
    }
    params = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(url, headers=headers, params=params)
    return response.json().get("access_token")

# Rotta principale per test
@app.route("/")
def home():
    return "✅ API di iscritti attiva. Usa /registrants?webinar_id=IDWEBINAR"

# Rotta per ottenere gli iscritti
@app.route("/registrants")
def get_registrants():
    webinar_id = request.args.get("webinar_id")
    if not webinar_id:
        return jsonify({"error": "Webinar ID mancante"}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Access token non ottenuto"}), 401

    zoom_url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(zoom_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Errore nel recupero dei dati Zoom"}), 500

    registrants = response.json().get("registrants", [])
    results = []
    for r in registrants:
        results.append({
            "first_name": r.get("first_name"),
            "last_name": r.get("last_name"),
            "email": r.get("email"),
            "join_url": r.get("join_url")
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False)
