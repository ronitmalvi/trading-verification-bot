import os
from support_service import resolve_ticket
from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, Request
from google_sheet_service import verify_account
from support_service import (
    create_ticket)


from whatsapp_service import (
    send_text_message,
    send_main_menu,
    send_broker_buttons,
    send_verified_menu,
    send_support_ticket_to_admin
)

from session_manager import (
    get_state,
    set_state,
    get_session,
    mark_verified
)


app = FastAPI()

VERIFY_TOKEN = "tradingbot123"

@app.get("/sheet-test/{account_number}")
def sheet_test(account_number: str):

    result = verify_account(
        account_number
    )

    return {
        "account": account_number,
        "verified": result
    }

@app.get("/")
def home():

    return {
        "message": "Trading Verification Bot Running"
    }

@app.get("/db-test")
def db_test():

    from database import SessionLocal
    from models import UserSession

    db = SessionLocal()

    try:

        session = UserSession(
            phone_number="919999999999",
            state="TEST"
        )

        db.add(session)
        db.commit()

        return {
            "status": "database connected"
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:
        db.close()

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
        # ADMIN RESOLUTION COMMAND
        # ==================================

        ADMIN_PHONE = os.getenv(
            "ADMIN_PHONE"
        )

        if phone == ADMIN_PHONE:

            if (
                message_text and
                message_text.startswith("RESOLVE ")
            ):

                parts = (
                    message_text.split(
                        " ",
                        2
                    )
                )

                if len(parts) < 3:

                    send_text_message(
                        phone,
                        "Format: RESOLVE <ticket_id> <message>"
                    )

                    return {"status": "received"}

                ticket_id = int(parts[1])

                resolution = parts[2]

                ticket = resolve_ticket(
                    ticket_id,
                    resolution
                )

                if not ticket:

                    send_text_message(
                        phone,
                        "Ticket not found."
                    )

                    return {"status": "received"}

                send_text_message(
                    ticket["user_phone"],
                    f"""
        ✅ Support Update

        Ticket ID: {ticket["id"]}

        {resolution}
        """
                )

                send_text_message(
                    phone,
                    f"Ticket {ticket["id"]} resolved."
                )

                return {"status": "received"}
        # ==================================
        # RESET CONVERSATION
        # ==================================

        if (
            message_text and
            message_text.lower() in [
                "hi",
                "hii",
                "hiii",
                "hello",
                "hey",
                "start",
                "menu",
                "restart",
                "reset"
            ]
        ):

            session = get_session(phone)

            if (
                session and
                session.is_verified
            ):

                send_verified_menu(phone)

            else:

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
                    "💬 Please describe your issue in detail."
                )

                set_state(
                    phone,
                    "WAITING_SUPPORT_QUERY"
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

            broker = session.broker

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

            result = verify_account(account_number)

            if result:

                mark_verified(phone,account_number)

                send_text_message(
                    phone,
                    """✅ Account Verified

        Welcome to Premium Access."""
                )

                send_verified_menu(phone)

            else:

                send_text_message(
                    phone,
                    """❌ Verification Failed

        Account not found or not eligible."""
                )
            set_state(
                phone,
                "VERIFICATION_COMPLETE",
                broker=broker,
                account=account_number
            )

            return {"status": "received"}
        
        if user_state == "WAITING_SUPPORT_QUERY":

            ticket_id = create_ticket(
                phone,
                message_text
            )

            send_support_ticket_to_admin(
                ticket_id,
                phone,
                message_text
            )

            send_text_message(
                phone,
                f"""
        ✅ Support Request Submitted

        Ticket ID: {ticket_id}

        Our team will contact you shortly.
        """
            )

            set_state(
                phone,
                "MAIN_MENU"
            )

            return {"status": "received"}
            
        session = get_session(phone)

        if (
            session and
            session.is_verified
        ):

            if selected_option == "PREMIUM":

                send_text_message(
                    phone,
                    """👥 Premium Access

        Telegram:
        https://t.me/yourgroup

        WhatsApp:
        https://chat.whatsapp.com/xxxxx
        """
                )

            elif selected_option == "FAQ":

                send_text_message(
                    phone,
                    """📘 FAQs

        Your FAQs here.
        """
                )

            elif selected_option == "SUPPORT":

                send_text_message(
                    phone,
                    "💬 Please describe your issue."
                )

                set_state(
                    phone,
                    "WAITING_SUPPORT_QUERY"
                )

            return {"status": "received"}


    except Exception as e:

        print("ERROR")
        print(str(e))

    return {"status": "received"}