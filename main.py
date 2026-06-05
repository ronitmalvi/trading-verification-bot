from fastapi import FastAPI, Request
import requests
import os

from session_manager import (
    get_state,
    set_state,
    get_session
)

app = FastAPI()

VERIFY_TOKEN = "tradingbot123"


def send_whatsapp_message(phone, message):

    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    url = f"https://graph.facebook.com/v23.0/{phone_number_id}/messages"

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


@app.post("/webhook")
async def receive_message(request: Request):

    data = await request.json()

    print("\n========== WHATSAPP EVENT ==========")
    print(data)

    try:

        if "entry" not in data:
            return {"status": "received"}

        changes = data["entry"][0].get(
            "changes",
            []
        )

        if not changes:
            return {"status": "received"}

        value = changes[0].get(
            "value",
            {}
        )

        if "messages" not in value:
            return {"status": "received"}

        message = value["messages"][0]

        phone = message["from"]

        if "text" not in message:
            return {"status": "received"}

        text = message["text"]["body"].strip()

        print(f"Phone: {phone}")
        print(f"Message: {text}")

        user_state = get_state(phone)

        # =========================
        # START
        # =========================

        if user_state == "START":

            send_whatsapp_message(
                phone,
                """🚀 Welcome to Trading Verification Portal

Reply with:

1 - Verify Trading Account
2 - FAQs
3 - Terms & Conditions
4 - Privacy Policy
5 - Support"""
            )

            set_state(
                phone,
                "MAIN_MENU"
            )

            return {"status": "received"}

        # =========================
        # MAIN MENU
        # =========================

        if user_state == "MAIN_MENU":

            if text == "1":

                send_whatsapp_message(
                    phone,
                    """Select Broker

1 - XM Global
2 - Delta Exchange"""
                )

                set_state(
                    phone,
                    "WAITING_BROKER"
                )

            else:

                send_whatsapp_message(
                    phone,
                    "Please select a valid option."
                )

            return {"status": "received"}

        # =========================
        # BROKER SELECTION
        # =========================

        if user_state == "WAITING_BROKER":

            if text == "1":

                send_whatsapp_message(
                    phone,
                    "Please enter your XM Trading Account Number"
                )

                set_state(
                    phone,
                    "WAITING_ACCOUNT",
                    broker="XM"
                )

            elif text == "2":

                send_whatsapp_message(
                    phone,
                    "Please enter your Delta Trading Account Number"
                )

                set_state(
                    phone,
                    "WAITING_ACCOUNT",
                    broker="DELTA"
                )

            else:

                send_whatsapp_message(
                    phone,
                    "Invalid broker selection."
                )

            return {"status": "received"}

        # =========================
        # ACCOUNT NUMBER
        # =========================

        if user_state == "WAITING_ACCOUNT":

            session = get_session(phone)

            broker = session.get("broker")

            account_number = text

            send_whatsapp_message(
                phone,
                f"""🔍 Verifying Account

Broker: {broker}
Account Number: {account_number}

Please wait..."""
            )

            send_whatsapp_message(
                phone,
                """✅ Account Received

Verification API will be connected next."""
            )

            set_state(
                phone,
                "VERIFICATION_COMPLETE",
                broker=broker,
                account=account_number
            )

            return {"status": "received"}

    except Exception as e:

        print("ERROR:")
        print(str(e))

    return {"status": "received"}