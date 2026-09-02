import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from datetime import datetime, timedelta

app = Flask(__name__)

# ==== Twilio credentials (Railway ke "Variables" tab me set karna hai) ====
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")   # Twilio ka phone number, jaise +1XXXXXXXXXX
CALL_TO_NUMBER = os.environ.get("CALL_TO_NUMBER")           # Jispe call jani hai, jaise +91XXXXXXXXXX
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme123")    # extension aur backend ke beech simple auth

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Cooldown taaki spam calls na ho (backend side pe bhi safety)
last_call_time = None
COOLDOWN_SECONDS = 20


@app.route("/", methods=["GET"])
def home():
    return {"status": "TG Call backend is running"}


@app.route("/trigger-call", methods=["POST"])
def trigger_call():
    global last_call_time

    data = request.get_json(silent=True) or {}

    # Simple secret check — extension bhi yahi key bhejega
    if data.get("secret") != SECRET_KEY:
        return jsonify({"error": "unauthorized"}), 401

    now = datetime.utcnow()
    if last_call_time and (now - last_call_time).total_seconds() < COOLDOWN_SECONDS:
        return jsonify({"status": "skipped_cooldown"}), 200

    try:
        call = client.calls.create(
            to=CALL_TO_NUMBER,
            from_=TWILIO_FROM_NUMBER,
            twiml='<Response><Say voice="alice">Naya message aaya hai apke Telegram group mein. Please check karein.</Say></Response>'
        )
        last_call_time = now
        return jsonify({"status": "call_triggered", "call_sid": call.sid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
