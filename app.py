@app.route("/webhook", methods=["POST"])
def webhook():
    if request.content_type == "application/json":
        # Untuk 360dialog (kamu sudah buat ini)
        data = request.get_json()
        try:
            message = data["messages"][0]["text"]["body"]
            sender = data["messages"][0]["from"]
        except Exception as e:
            print("Gagal parsing dari 360dialog:", e)
            return jsonify({"error": "Invalid 360dialog payload"}), 400

    elif request.content_type == "application/x-www-form-urlencoded":
        # Untuk Twilio
        try:
            message = request.form.get("Body")
            sender = request.form.get("From")
            print(f"Pesan dari {sender}: {message}")
        except Exception as e:
            print("Gagal parsing dari Twilio:", e)
            return jsonify({"error": "Invalid Twilio payload"}), 400
    else:
        return jsonify({"error": "Unsupported Content-Type"}), 415

    # Proses GPT seperti biasa
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah chatbot pelayanan ketenagakerjaan. Jawablah ringkas, ramah, dan sopan."},
                {"role": "user", "content": message}
            ]
        )
        response = completion.choices[0].message.content.strip()

        # Balas ke Twilio (pakai TwiML) atau 360dialog (pakai POST)
        if "twilio" in request.form.get("ApiVersion", "").lower() or "whatsapp" in sender.lower():
            from twilio.twiml.messaging_response import MessagingResponse
            twiml = MessagingResponse()
            twiml.message(response)
            return str(twiml), 200, {'Content-Type': 'application/xml'}

        else:
            # Default: kirim ke 360dialog
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
            return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error GPT atau pengiriman:", e)
        return jsonify({"error": str(e)}), 500
