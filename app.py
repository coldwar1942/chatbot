import os, sys
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "my_secure_token"

PAGE_ACCESS_TOKEN = "EAAQCN5Nd2sMBOZBBVpbNb1ze6SsFfHufy9qaP9ZCZCYoa9rIgcaltYSPD9LXSTl9TEb4mmm8xkWrhqWbOV6MWKnRZBfsIuZC7HiIeoY80mbkuZB8UP3bwnTBUyrZBBT68JmprZBSOqYD9CLzeQcNAlQamJXJIrMlmRttO5ZAY8n3oMi3uku9sSwQ5lhRuW1Ov95IYFVmfjy05S3nZAb3YGTAZDZD"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': # ✅ ตรวจสอบ Verify Token
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verified!")
            return challenge, 200 # ส่งค่า challenge กลับให้ Facebook
        else:
            return "❌ Forbidden", 403

    elif request.method == 'POST': # ✅ รับข้อความจาก Facebook
        body = request.get_json()
        print("📩 Received POST:", body)

        if body and body.get("object") == "page":
            for entry in body.get("entry", []):
                for event in entry.get("messaging", []):
                    sender_id = event["sender"]["id"]
                    if "message" in event and "text" in event["message"]:
                        user_message = event["message"]["text"]
                        print(f"👤 User ({sender_id}): {user_message}")

                        send_message(sender_id, f"You said: {user_message}")

            return "EVENT_RECEIVED", 200

        return "Not Found", 404

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"📨 Sent message to {recipient_id}: {text}")
    print(f"🔹 Facebook Response: {response.status_code} {response.text}")



if __name__ == '__main__' :
    app.run(port=8080)



