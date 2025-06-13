from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Gunakan environment variable di Railway untuk keamanan
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Webhook aktif untuk Twilio WhatsApp ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    # Ambil data dari form (karena Twilio kirim sebagai x-www-form-urlencoded)
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")

    print(f"Pesan masuk dari {sender}: {incoming_msg}")

    # Respons default kalau terjadi error
    response_text = "Maaf, terjadi kesalahan. Coba lagi ya."

    try:
        # Panggil OpenAI GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah singkat, ramah, dan sopan.",
                },
                {"role": "user", "content": incoming_msg},
            ]
        )
        response_text = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error saat memanggil OpenAI:", e)

    # Buat Twilio MessagingResponse
    twiml = MessagingResponse()
    twiml.message(response_text)

    return str(twiml), 200, {"Content-Type": "application/xml"}

# Untuk Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
