from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
D360_API_KEY = os.environ.get("D360_API_KEY")
D360_SEND_URL = "https://waba-sandbox.360dialog.io/v1/messages"

@app.route("/", methods=["GET"])
def home():
    return "Webhook aktif!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["messages"][0]["text"]["body"]
        sender = data["messages"][0]["from"]

        # Buat jawaban dari GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah dengan ringkas dan sopan."},
                {"role": "user", "content": message}
            ]
        )

        response = completion.choices[0].message.content.strip()

        # Kirim ke WhatsApp
        headers = {
            "D360-API-KEY": D360_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "recipient_type": "individual",
            "to": sender,
            "type": "text",
            "text": {"body": response}
        }

        requests.post(D360_SEND_URL, headers=headers, json=payload)

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "ok"}), 200
