import os
import requests


def get_headers():

    token = os.getenv("WHATSAPP_TOKEN")

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def get_url():

    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    return f"https://graph.facebook.com/v23.0/{phone_number_id}/messages"


# def send_text_message(phone, message):

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone,
#         "type": "text",
#         "text": {
#             "body": message
#         }
#     }

#     response = requests.post(
#         get_url(),
#         headers=get_headers(),
#         json=payload
#     )

#     print(response.status_code)
#     print(response.text)


def send_text_message(phone, message):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        get_url(),
        headers=get_headers(),
        json=payload
    )

    print("========== SEND MESSAGE ==========")
    print(response.status_code)
    print(response.text)
    
# def send_main_menu(phone):

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone,
#         "type": "interactive",
#         "interactive": {
#             "type": "button",
#             "header": {
#                 "type": "text",
#                 "text": "Trading Verification Portal"
#             },
#             "body": {
#                 "text": "Please choose an option"
#             },
#             # "footer": {
#             #     "text": "Powered by Trading Verification Bot"
#             # },
#             "action": {
#                 "button": "Open Menu",
#                 "sections": [
#                     {
#                         "title": "Main Menu",
#                         "rows": [
#                             {
#                                 "id": "VERIFY_ACCOUNT",
#                                 "title": "Verify Trading Account"
#                             },
#                             {
#                                 "id": "FAQ",
#                                 "title": "FAQs"
#                             },
#                             {
#                                 "id": "SUPPORT",
#                                 "title": "Support"
#                             }
#                         ]
#                     }
#                 ]
#             }
#         }
#     }

#     requests.post(
#         get_url(),
#         headers=get_headers(),
#         json=payload
#     )
def send_main_menu(phone):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "🚀 Welcome to Trading Verification Portal\n\nPlease select an option."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "VERIFY_ACCOUNT",
                            "title": "✅ Verify Account"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "FAQ",
                            "title": "📘 FAQs"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "SUPPORT",
                            "title": "💬 Support"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(
        get_url(),
        headers=get_headers(),
        json=payload
    )

    print("MAIN MENU RESPONSE")
    print(response.status_code)
    print(response.text)
def send_broker_buttons(phone):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Select Broker"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "XM",
                            "title": "📈 XM Global"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "DELTA",
                            "title": "⚡ Delta Exchange"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "BACK_MAIN",
                            "title": "⬅ Back"
                        }
                    }
                ]
            }
        }
    }

    requests.post(
        get_url(),
        headers=get_headers(),
        json=payload
    )

def send_verified_menu(phone):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "🎉 Account Already Verified\n\nChoose an option."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "PREMIUM",
                            "title": "👥 Premium"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "FAQ",
                            "title": "📘 FAQs"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "SUPPORT",
                            "title": "💬 Support"
                        }
                    }
                ]
            }
        }
    }

    requests.post(
        get_url(),
        headers=get_headers(),
        json=payload
    )

def send_support_ticket_to_admin(
    ticket_id,
    user_phone,
    query
):

    admin_phone = os.getenv(
        "ADMIN_PHONE"
    )

    send_text_message(
        admin_phone,
        f"""
🚨 New Support Ticket

Ticket ID: {ticket_id}

User:
{user_phone}

Issue:
{query}
"""
    )