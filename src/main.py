import json
from src.gmail_service import get_gmail_service, fetch_unread_emails
from src.email_parser import parse_email
from src.sheets_service import get_sheets_service, append_to_sheet

from googleapiclient.errors import HttpError

from config import SHEET_ID, SHEET_RANGE

print("DEBUG SHEET_ID =", SHEET_ID)
print("DEBUG SHEET_RANGE =", SHEET_RANGE)

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
    print("OAuth complete, starting email processing...")

    state = load_state()
    print("Fetching unread emails...")
    emails = fetch_unread_emails(gmail)
    print("Fetched:", emails)
    if not emails:
        print("No new unread emails.")
        return

    for email in emails:
        msg_id = email['id']

        if msg_id == state["last_processed_id"]:
            continue  # skip duplicates

        try:
            print("Parsing:", msg_id)
            sender, subject, date, body = parse_email(gmail, msg_id)
            print("Parsed email:", sender, subject)
            if len(body) > 49000:
                print("Body too long, truncating...")
                body = body[:49000] + " ... [TRUNCATED]"

            append_to_sheet(sheets, SHEET_ID, SHEET_RANGE, [sender, subject, date, body])

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
