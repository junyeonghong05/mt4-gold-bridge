from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

latest_data = {}


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "MT4 Gold Bridge",
        "version": "2.0"
    })


@app.route("/mt4", methods=["POST"])
def mt4():
    global latest_data

    # JSON 또는 MT4 form-data 모두 허용
    data = request.get_json(silent=True)

    if data is None:
        data = request.form.to_dict()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No MT4 data received"
        }), 400

    latest_data = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "data": data
    }

    return jsonify({
        "status": "ok",
        "message": "MT4 data received",
        "received_at": latest_data["received_at"]
    })


@app.route("/latest", methods=["GET"])
def latest():
    if not latest_data:
        return jsonify({
            "status": "waiting",
            "message": "No MT4 data received yet"
        })

    return jsonify(latest_data)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "MT4 Gold Bridge"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
