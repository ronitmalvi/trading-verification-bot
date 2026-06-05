from fastapi import FastAPI, Request
import os

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

    print(data)

    return {
        "status": "received"
    }