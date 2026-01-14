import json
from src.gmail_service import get_gmail_service, fetch_unread_emails
from src.email_parser import parse_email
from src.sheets_service import get_sheets_service, append_to_sheet

from googleapiclient.errors import HttpError

SHEET_ID = "YOUR_GOOGLE_SHEET_ID"

def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except:
        return {"last_processed_id": ""}

def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f)

def main():
    gmail = get_gmail_service()
    sheets = get_sheets_service()

    state = load_state()

    emails = fetch_unread_emails(gmail)

    if not emails:
        print("No new unread emails.")
        return

    for email in emails:
        msg_id = email['id']

        if msg_id == state["last_processed_id"]:
            continue  # skip duplicates

        try:
            sender, subject, date, body = parse_email(gmail, msg_id)
            append_to_sheet(sheets, SHEET_ID, [sender, subject, date, body])

            # Mark email as read
            gmail.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            state["last_processed_id"] = msg_id
            save_state(state)

        except HttpError as err:
            print("API error:", err)

if __name__ == "__main__":
    main()
