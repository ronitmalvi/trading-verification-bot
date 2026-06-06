from fastapi import FastAPI, Request

from whatsapp_service import (
    send_text_message,
    send_main_menu,
    send_broker_buttons
)

from session_manager import (
    get_state,
    set_state,
    get_session
)

from xm_service import (verify_xm_account)

app = FastAPI()

VERIFY_TOKEN = "tradingbot123"


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

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {
        "error": "verification failed"
    }


@app.post("/webhook")
async def receive_message(request: Request):

    data = await request.json()

    print(data)

    try:

        value = (
            data["entry"][0]
            ["changes"][0]
            ["value"]
        )

        phone = None
        selected_option = None
        message_text = None

        if "messages" not in value:
            return {"status": "received"}

        message = value["messages"][0]

        phone = message["from"]

        # ======================
        # LIST MENU CLICK
        # ======================

        if (
            message.get("type")
            == "interactive"
        ):

            interactive = message["interactive"]

            if (
                interactive["type"]
                == "list_reply"
            ):

                selected_option = (
                    interactive["list_reply"]["id"]
                )

            elif (
                interactive["type"]
                == "button_reply"
            ):

                selected_option = (
                    interactive["button_reply"]["id"]
                )

        elif "text" in message:

            message_text = (
                message["text"]["body"]
                .strip()
            )
        
        # ==================================
        # RESET CONVERSATION
        # ==================================

        if (
            message_text and
            message_text.lower() in [
                "hi",
                "hello",
                "start",
                "menu",
                "restart",
                "reset"
            ]
        ):

            set_state(
                phone,
                "MAIN_MENU"
            )

            send_main_menu(phone)

            return {"status": "received"}

        user_state = get_state(phone)

        # ======================
        # START
        # ======================

        if user_state == "START":

            send_main_menu(phone)

            set_state(
                phone,
                "MAIN_MENU"
            )

            return {"status": "received"}

        # ======================
        # MAIN MENU
        # ======================

        if user_state == "MAIN_MENU":

            if selected_option == "VERIFY_ACCOUNT":

                send_broker_buttons(phone)

                set_state(
                    phone,
                    "WAITING_BROKER"
                )

            elif selected_option == "FAQ":

                send_text_message(
                    phone,
                    "FAQs coming soon."
                )

            # elif selected_option == "TERMS":

            #     send_text_message(
            #         phone,
            #         "Terms & Conditions coming soon."
            #     )

            # elif selected_option == "PRIVACY":

            #     send_text_message(
            #         phone,
            #         "Privacy Policy coming soon."
            #     )

            elif selected_option == "SUPPORT":

                send_text_message(
                    phone,
                    "Support coming soon."
                )

            return {"status": "received"}

        # ======================
        # BROKER BUTTONS
        # ======================

        if user_state == "WAITING_BROKER":

            if selected_option == "XM":

                send_text_message(
                    phone,
                    "Please enter your XM Global Trading Account Number"
                )

                set_state(
                    phone,
                    "WAITING_ACCOUNT",
                    broker="XM Global"
                )

            elif selected_option == "DELTA":

                send_text_message(
                    phone,
                    "Please enter your Delta Exchange Trading Account Number"
                )

                set_state(
                    phone,
                    "WAITING_ACCOUNT",
                    broker="Delta Exchange"
                )
            
            elif selected_option == "BACK_MAIN":

                send_main_menu(phone)

                set_state(
                    phone,
                    "MAIN_MENU"
                )

            return {"status": "received"}

        # ======================
        # ACCOUNT INPUT
        # ======================

        if user_state == "WAITING_ACCOUNT":

            account_number = message_text.strip()

            if not account_number.isdigit():

                send_text_message(
                    phone,
                    "Please enter a valid numeric trading account number."
                )

                return {"status": "received"}

            session = get_session(phone)

            broker = session["broker"]

            send_text_message(
                phone,
                f"""🔍 Verifying Account

                Broker: {broker}
                Account Number: {account_number}

                Please wait..."""
            )

            # send_text_message(
            #     phone,
            #     "✅ Account Received\n\nXM API integration will be connected next."
            # )

            result = verify_xm_account(
                account_number
            )

            if result["verified"]:

                send_text_message(
                    phone,
                    f"""✅ Account Verified

            Broker: {broker}
            Account: {account_number}
            """
                )

            else:

                send_text_message(
                    phone,
                    "❌ Account verification failed."
                )

            set_state(
                phone,
                "VERIFICATION_COMPLETE",
                broker=broker,
                account=account_number
            )

            return {"status": "received"}

    except Exception as e:

        print("ERROR")
        print(str(e))

    return {"status": "received"}