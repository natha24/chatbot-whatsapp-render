from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
TWILIO_SEND_BACK = False  # Ubah ke True jika ingin membalas langsung via Twilio

@app.route("/", methods=["GET"])
def home():
    return "Webhook aktif!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        message = request.form.get("Body")
        sender = request.form.get("From")

        print("Pesan:", message)
        print("Dari:", sender)

        if not message or not sender:
            return jsonify({"status": "ignored"}), 200

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah ringkas, ramah, dan sopan."},
                {"role": "user", "content": message}
            ]
        )
        response = completion.choices[0].message.content.strip()
        print("Balasan:", response)

        # Jika ingin balas ke Twilio, tambahkan logika di sini
        return response, 200

    except Exception as e:
        print("Terjadi error:", e)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
