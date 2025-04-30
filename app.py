from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Backend Zoom operativo."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


@app.route("/")
def home():
    return "✅ API di iscritti attiva. Usa /api/registrants?id=IDWEBINAR"
