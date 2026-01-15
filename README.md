# gmail_to_sheets

📧 Gmail → Google Sheets Automation

A Python-based automation script that fetches unread Gmail messages, extracts structured data, and appends it to Google Sheets using OAuth authentication for both Gmail and Sheets APIs.

🧩 Architecture Overview

Below is a simple architecture diagram (hand-drawn style):

                +----------------------------+
                |        Gmail Inbox        |
                +-------------+--------------+
                              |
                              | Fetch unread emails (Gmail API)
                              v
                  +------------------------+
                  |   gmail_service.py     |
                  +------------------------+
                              |
                              | Parse metadata + body
                              v
                  +------------------------+
                  |   email_parser.py      |
                  +------------------------+
                              |
                              | Append row to sheet (Sheets API)
                              v
                  +------------------------+
                  |  sheets_service.py     |
                  +------------------------+
                              |
                              v
                +-----------------------------+
                |     Google Sheets Output    |
                +-----------------------------+
                              |
                              | Save last processed email ID
                              v
                +-----------------------------+
                |        state.json           |
                +-----------------------------+

🔧 Step-by-Step Setup Instructions

Follow exactly in this order:

1️⃣ Clone the repository
git clone https://github.com/your-username/gmail-to-sheets.git
cd gmail-to-sheets

2️⃣ Create a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Enable APIs in Google Cloud Console

Go to:

https://console.cloud.google.com/


Enable:

✔ Gmail API
✔ Google Sheets API

5️⃣ Configure OAuth consent screen

User type: External

App name: Gmail to Sheets Automation

Add scopes:

https://www.googleapis.com/auth/gmail.modify

https://www.googleapis.com/auth/spreadsheets

Add your Gmail under Test Users

6️⃣ Download OAuth client credentials

Download from:

APIs & Services > Credentials > OAuth 2.0 Client IDs


Place file as:

credentials/credentials.json


⚠️ DO NOT commit this file.

7️⃣ Add your Google Sheet ID

Open your sheet URL:

https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit


Copy <SHEET_ID> and update config.py:

SHEET_ID = "your_sheet_id_here"
SHEET_RANGE = "Sheet1!A:D"

8️⃣ Run the script
python -m src.main


It will open a browser twice:

once for Gmail OAuth

once for Sheets OAuth

After authorization, script will start processing automatically.

🔐 OAuth Flow Explained

This project uses OAuth 2.0 installed application flow.

How it works:

The script launches a local server using:

flow.run_local_server()


Google shows a consent screen.

User grants permissions.

The script receives an authorization code.

This code is exchanged for:

access token

refresh token

Why this method is used?

✔ Safe
✔ Google-recommended for local apps
✔ Refresh token avoids repeated logins
✔ Works without exposing password

🔁 Duplicate Prevention Logic

The script prevents reprocessing the same email using this flow:

Every fetched email has a unique msg_id.

After processing, the script stores:

{ "last_processed_id": "<msg_id>" }


in state.json.

When running again, script compares each fetched email ID with saved ID:

if msg_id == state["last_processed_id"]:
    continue


As soon as it finds the previously processed message → the loop skips it.

💾 State Persistence Method
File used:
state.json

What it stores:
{
  "last_processed_id": "19b2b5e0d8ffb912"
}

Why this approach?

✔ Very simple
✔ Persistent between runs
✔ No database required
✔ Works offline

🧠 Challenge Faced & How I Solved It
Challenge:

Google Sheets API returned:

Your input contains more than the maximum of 50000 characters in a single cell.


Some marketing emails contain huge HTML bodies which exceed Google’s row limit.

Solution implemented:

I added truncation logic in email_parser.py:

if len(body) > 50000:
    body = body[:50000] + " ...[TRUNCATED]"


This ensures:

✔ Script never crashes
✔ All essential metadata still gets saved
✔ No API errors from Sheets

⚠️ Limitations of the Current Solution
❌ 1. Not production-ready authentication

Uses OAuth installed-app flow, not service accounts.
User must manually authorize once.

❌ 2. State tracking is minimal

Only stores last processed email ID instead of full history.

❌ 3. Cannot handle extremely complex email bodies

HTML-heavy emails are only partially processed.

❌ 4. Script processes only unread emails

If email is already read, it will never be processed.

❌ 5. No scheduling / automation built-in

User must run the script manually.
(But can be automated using cron / Task Scheduler.)

📎 Attachments Included

This repository includes a folder:

proof/
  ├── screenshots/
  └── recording/


Screenshots include:

OAuth flow

Terminal output logs

Gmail unread before & after

Google Sheet with appended rows

OAuth consent screen screenshot

Script output screenshot

▶️ Demo Video Requirements

A 2–3 min video must show:

Project folder structure

Running the script

OAuth authentication

Email parsing logs

Rows added in Google Sheet

Second run showing no duplicates

🚀 Bonus Features Implemented

✔ Body truncation for large emails
✔ HTML → plain text conversion
✔ OAuth token caching
✔ Detailed console logging

⚠ Limitations

🔸 Cannot process emails exceeding 50k characters (Google Sheets limit)
🔸 Gmail API quota limits apply
🔸 Requires first-time OAuth login manually
🔸 Some HTML emails may strip formatting

📌 Future Enhancements

Add filtering by subject keywords

Add label extraction

Exclude “no-reply” emails

Process emails only within last 24 hours

Add Docker support

Add retry logic for unstable networks


👨‍💻 Author
Thushank Sachin Bagal
Full Stack Developer (Python | MERN | Cloud)
