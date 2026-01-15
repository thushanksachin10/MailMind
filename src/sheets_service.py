from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import SHEET_ID, SHEET_RANGE
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds = None

    # Load existing token
    if os.path.exists("token_sheets.pickle"):
        with open("token_sheets.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no token or invalid token, start OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8081, open_browser=True)


        # Save the new token
        with open("token_sheets.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("sheets", "v4", credentials=creds)

def append_to_sheet(service, sheet_id, sheet_range, row_data):
    sheet = service.spreadsheets()
    body = {"values": [row_data]}

    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range=sheet_range,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result
