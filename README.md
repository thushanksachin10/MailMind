# gmail_to_sheets

📧 Gmail → Google Sheets Automation (Python)

Automate importing unread Gmail messages into Google Sheets using Python + Google APIs.

📌 Overview

This project automates the process of fetching unread Gmail messages and logging them into a Google Sheet using Python, Gmail API, and Google Sheets API.

✔ Reads unread emails from the Inbox
✔ Extracts From, Subject, Date, and Body
✔ Appends structured rows to a Google Sheet
✔ Marks emails as read after processing
✔ Prevents duplicates using persistent state tracking

📂 Project Structure
gmail-to-sheets/
│
├── src/
│   ├── gmail_service.py        # Gmail API authentication + fetch unread emails
│   ├── sheets_service.py       # Sheets API + append rows
│   ├── email_parser.py         # Extract details from each email
│   └── main.py                 # Main automation flow
│
├── credentials/
│   └── credentials.json        # OAuth client secret (not committed)
│
├── config.py
├── requirements.txt
├── .gitignore
└── README.md

🛠 Setup Instructions (Step-by-Step)
1️⃣ Clone the Repository
git clone https://github.com/your-username/gmail-to-sheets.git
cd gmail-to-sheets

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Enable APIs in Google Cloud Console

Go to:

👉 https://console.cloud.google.com/apis/library

Enable:

Gmail API

Google Sheets API

5️⃣ Create OAuth Credentials

Navigate:

APIs & Services → Credentials → Create Credentials → OAuth Client ID

Choose:

Application Type: Desktop App

Download JSON file

Rename to:

credentials.json


Place inside:

credentials/credentials.json


⚠ Do NOT commit this file.

6️⃣ Update config.py
SHEET_ID = "YOUR_GOOGLE_SHEET_ID"
SHEET_RANGE = "Sheet1!A:D"
GMAIL_USER = "me"


Find the Google Sheet ID here:

https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit

7️⃣ Run Automation Script
python -m src.main


You will see:

Please visit this URL to authorize this application...


Log in → grant permissions → script starts processing emails.

🧠 How Duplicate Prevention Works

A state.json file stores the last processed Gmail message ID:

{
  "last_processed_id": "19b26cb3f8324c53"
}


✔ Prevents reprocessing
✔ Lightweight
✔ Local & persistent
✔ No database required

📈 Data Logged to Google Sheets
Column	Description
From	Sender email
Subject	Email subject
Date	Timestamp received
Content	Parsed + cleaned email body

Supports HTML → Text conversion and body truncation to remain under Google Sheets cell size limits.

📸 Proof of Execution

Screenshots required in /proof/ directory:

Gmail inbox with unread messages

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