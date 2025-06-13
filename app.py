from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Gunakan variabel lingkungan untuk kunci API
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Webhook aktif!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        message = request.form.get("Body")
        sender = request.form.get("From")

        print(f"Pesan: {message}")
        print(f"Dari: {sender}")

        # Format baru OpenAI API (>=1.0.0)
        client = openai.OpenAI()
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah singkat, ramah, dan sopan."},
                {"role": "user", "content": message}
            ]
        )

        reply = chat_response.choices[0].message.content.strip()

        # Balas pesan ke Twilio
        from twilio.twiml.messaging_response import MessagingResponse
        response = MessagingResponse()
        response.message(reply)
        return str(response)

    except Exception as e:
        print("Terjadi error:", e)
        return jsonify({"error": str(e)}), 500

# Untuk Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
