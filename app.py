from flask import Flask, request
import openai
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")  # simpan di Railway

@app.route("/", methods=["GET"])
def index():
    return "Webhook aktif!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Ambil isi pesan dari request POST Twilio
        incoming_msg = request.form.get("Body")
        sender = request.form.get("From")

        # Panggil OpenAI untuk menjawab
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten pelayanan ketenagakerjaan. Jawab pertanyaan dengan singkat, ramah, dan informatif."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        response_text = completion.choices[0].message.content.strip()

        # Balas ke Twilio (otomatis kirim balik ke pengirim)
        twilio_resp = MessagingResponse()
        twilio_resp.message(response_text)

        return str(twilio_resp)

    except Exception as e:
        print("Terjadi error:", e)
        return "Error", 500

# Jalankan di Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
