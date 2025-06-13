from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Webhook aktif!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("Headers:", request.headers)
        print("Content-Type:", request.content_type)

        # Coba baca semua data yang masuk
        print("Raw data:", request.data)
        print("Form data:", request.form)
        print("JSON:", request.get_json(force=False, silent=True))

        # Ambil pesan dan pengirim dari Twilio (pakai form, bukan JSON)
        message = request.form.get("Body")
        sender = request.form.get("From")

        print("Pesan:", message)
        print("Dari:", sender)

        if not message:
            return "No message received", 400

        # Proses ke GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah dengan sopan, ringkas, dan ramah."},
                {"role": "user", "content": message}
            ]
        )
        response = completion.choices[0].message.content.strip()

        # Balas ke Twilio pakai XML
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>""", 200, {'Content-Type': 'application/xml'}

    except Exception as e:
        print("Terjadi error:", e)
        return jsonify({"error": str(e)}), 500

# Untuk Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
