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

@app.route("/signal", methods=["GET"])
def signal():
    if not latest_data:
        return jsonify({
            "signal": "WAIT",
            "reason": "No MT4 data received yet"
        })

    d = latest_data.get("data", {})

    try:
    def clean_number(value):
        return float(str(value).replace("\\x00", "").replace("\x00", "")strip())
        bid = clean_number(d.get("bid", 0))
        rsi = clean_number(d.get("rsi", 50))
        ema20 = clean_number(d.get("ema20", 0))
        ema50 = clean_number(d.get("ema50", 0))
        h1_ema20 = clean_number(d.get("h1_ema20", 0))
        h1_ema50 = clean_number(d.get("h1_ema50", 0))
        h1_rsi = clean_number(d.get("h1_rsi", 50))
        h1_macd = clean_number(d.get("h1_macd", 0))
        h1_macd_signal = clean_number(d.get("h1_macd_signal", 0))
        macd = clean_number(d.get("macd", 0))
        macd_signal = clean_number(d.get("macd_signal", 0))
        bb_upper = clean_number(d.get("bb_upper", 0))
        bb_middle = clean_number(d.get("bb_middle", 0))
        bb_lower = clean_number(d.get("bb_lower", 0))
        atr = clean_number(d.get("atr", 0))

        long_score = 0
        short_score = 0
        reasons = []

        # EMA trend
        if ema20 > ema50:
            long_score += 2
            reasons.append("EMA bullish")
        elif ema20 < ema50:
            short_score += 2
            reasons.append("EMA bearish")

        # MACD
        if macd > macd_signal:
            long_score += 2
            reasons.append("MACD bullish")
        elif macd < macd_signal:
            short_score += 2
            reasons.append("MACD bearish")

        # RSI
        if rsi < 30:
            long_score += 2
            reasons.append("RSI oversold")
        elif rsi > 70:
            short_score += 2
            reasons.append("RSI overbought")
        elif rsi > 55:
            long_score += 1
        elif rsi < 45:
            short_score += 1

        # Bollinger Bands
        if bb_lower > 0 and bid <= bb_lower:
            long_score += 2
            reasons.append("Near lower Bollinger Band")

        if bb_upper > 0 and bid >= bb_upper:
            short_score += 2
            reasons.append("Near upper Bollinger Band")

        if bb_middle > 0:
            if bid > bb_middle:
                long_score += 1
            elif bid < bb_middle:
                short_score += 1

        # Final signal
        if (
    long_score == 6
    and h1_ema20 > h1_ema50
    and h1_rsi > 50
    and h1_macd > h1_macd_signal
):
    result = "STRONG LONG"

elif (
    long_score >= short_score + 2
    and long_score >= 4
    and h1_ema20 > h1_ema50
    and h1_rsi > 50
    and h1_macd > h1_macd_signal
):
    result = "LONG"

elif (
    short_score == 6
    and h1_ema20 < h1_ema50
    and h1_rsi < 50
    and h1_macd < h1_macd_signal
):
    result = "STRONG SHORT"

elif (
    short_score >= long_score + 2
    and short_score >= 4
    and h1_ema20 < h1_ema50
    and h1_rsi < 50
    and h1_macd < h1_macd_signal
):
    result = "SHORT"

else:
    result = "WAIT"

entry = bid

if result in ["SHORT", "STRONG SHORT"]:
    sl = entry + (atr * 1.0)
    tp1 = entry - (atr * 1.0)
    tp2 = entry - (atr * 2.0)

elif result in ["LONG", "STRONG LONG"]:
    sl = entry - (atr * 1.0)
    tp1 = entry + (atr * 1.0)
    tp2 = entry + (atr * 2.0)

else:
    sl = None
    tp1 = None
    tp2 = None

        return jsonify({
            "symbol": d.get("symbol"),
            "bid": bid,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "signal": result,
            "long_score": long_score,
            "short_score": short_score,
            "rsi": rsi,
            "ema20": ema20,
            "ema50": ema50,
            "macd": macd,
            "macd_signal": macd_signal,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "atr": atr,
            "reason": reasons,
            "received_at": latest_data.get("received_at")
        })

    except (ValueError, TypeError) as e:
        return jsonify({
            "signal": "ERROR",
            "message": str(e)
        }), 400
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
