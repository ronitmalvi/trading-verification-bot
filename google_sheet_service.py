import os
import json
import gspread

from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]


credentials_info = json.loads(
    os.getenv("GOOGLE_CREDENTIALS")
)

creds = Credentials.from_service_account_info(
    credentials_info,
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    os.getenv("GOOGLE_SHEET_ID")
).sheet1

def verify_account(account_number):

    records = sheet.get_all_records()

    for row in records:

        if str(row["Account Number"]) == str(account_number):

            if (
                str(row["KYC Verified"]).upper() == "YES"
                and
                str(row["Live Account"]).upper() == "YES"
            ):

                return True

            return False

    return False