from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_access_token():
    url = "https://zoom.us/oauth/token"
    payload = {
        "grant_type": "account_credentials",
        "account_id": os.getenv("ZOOM_ACCOUNT_ID")
    }
    auth = (os.getenv("ZOOM_CLIENT_ID"), os.getenv("ZOOM_CLIENT_SECRET"))
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=headers, data=payload, auth=auth)
    response.raise_for_status()
    return response.json()["access_token"]

@app.route("/api/registrants")
def registrants():
    webinar_id = request.args.get("id")
    if not webinar_id:
        return jsonify({"error": "Webinar ID mancante"}), 400

    try:
        token = get_access_token()
        url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json().get("registrants", [])
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"
