from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

latest_data = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "MT4 Gold Bridge"
    })

@app.route("/mt4", methods=["POST"])
def mt4():
    global latest_data

    data = request.get_json(silent=True)

    if data is None:
        data = request.form.to_dict()

    latest_data = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "data": data
    }

    return jsonify({
        "status": "ok",
        "message": "MT4 data received"
    })

@app.route("/latest", methods=["GET"])
def latest():
    if not latest_data:
        return jsonify({
            "status": "waiting",
            "message": "No MT4 data received yet"
        })

    return jsonify(latest_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
