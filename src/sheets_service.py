from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds = None
    
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    return build("sheets", "v4", credentials=creds)

def append_to_sheet(service, sheet_id, row_data):
    sheet = service.spreadsheets()
    body = {
        "values": [row_data]
    }

    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A:D",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

