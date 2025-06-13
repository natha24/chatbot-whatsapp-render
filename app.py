from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

openai.api_key = os.environ.get("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")
D360_API_KEY = os.environ.get("cfBAd3_sandbox")
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

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah ringkas, ramah, dan sopan."},
                {"role": "user", "content": message}
            ]
        )
        response = completion.choices[0].message.content.strip()

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
        print("Webhook error:", e)

    return jsonify({"status": "ok"}), 200

# ==== ADD THIS PART FOR RAILWAY ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
