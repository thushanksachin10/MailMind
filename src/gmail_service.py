from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None

    # Load token if exists
    if os.path.exists("token_gmail.pickle"):
        with open("token_gmail.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, create new login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=8082, open_browser=True)

        # Save token
        with open("token_gmail.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def fetch_unread_emails(service):
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=20
    ).execute()

    return results.get("messages", [])
