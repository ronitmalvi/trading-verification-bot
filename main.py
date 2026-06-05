from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

VERIFY_TOKEN = "tradingbot123"


def send_whatsapp_message(phone, message):

    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    url = (
        f"https://graph.facebook.com/v23.0/"
        f"{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("WhatsApp Response:")
    print(response.status_code)
    print(response.text)


@app.get("/")
def home():
    return {
        "message": "Trading Verification Bot Running"
    }


@app.get("/webhook")
def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
    ):
        return int(challenge)

    return {
        "error": "verification failed"
    }


@app.get("/test-message")
def test_message():

    send_whatsapp_message(
        "+917247069397",
        "Hello from Trading Verification Bot 🚀"
    )

    return {
        "status": "message sent"
    }


@app.post("/webhook")
async def receive_message(request: Request):

    data = await request.json()

    print("\n========== WHATSAPP EVENT ==========")
    print(data)

    try:

        if (
            "entry" in data
            and len(data["entry"]) > 0
        ):

            changes = data["entry"][0].get("changes", [])

            if len(changes) > 0:

                value = changes[0].get("value", {})

                if "messages" in value:

                    message = value["messages"][0]

                    phone = message["from"]

                    welcome_message = """
🚀 Welcome to Trading Verification Portal

1. Verify Trading Account

2. FAQs

3. Terms & Conditions

4. Privacy Policy

5. Support
"""

                    send_whatsapp_message(
                        phone,
                        welcome_message
                    )

    except Exception as e:
        print(str(e))

    return {"status": "received"}