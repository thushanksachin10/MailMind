# 📧 Gmail → Google Sheets Automation

A Python automation pipeline that fetches unread Gmail messages, parses structured data, and appends rows to Google Sheets — using OAuth 2.0 for secure, token-cached authentication.

---

## 🧩 Architecture

```
+----------------------------+
|        Gmail Inbox         |
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
              | Append row (Sheets API)
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
              | Persist last processed ID
              v
+-----------------------------+
|         state.json          |
+-----------------------------+
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/thushanksachin10/gmail_to_sheets.git
cd gmail_to_sheets
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Enable APIs in Google Cloud Console
Go to [console.cloud.google.com](https://console.cloud.google.com/) and enable:
- Gmail API
- Google Sheets API

### 5. Configure OAuth consent screen
- User type: **External**
- Add scopes: `gmail.modify` and `spreadsheets`
- Add your Gmail as a **Test User**

### 6. Download credentials
- Go to **APIs & Services → Credentials → OAuth 2.0 Client IDs**
- Download and save as `credentials/credentials.json`
- ⚠️ This file is in `.gitignore` — never commit it

### 7. Set your Sheet ID
Open your sheet URL:
```
https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit
```
Copy `<SHEET_ID>` and update `config.py`:
```python
SHEET_ID = "your_sheet_id_here"
SHEET_RANGE = "Sheet1!A:D"
```

### 8. Run
```bash
python -m src.main
```
A browser window will open for Gmail OAuth, then again for Sheets OAuth. After authorizing once, tokens are cached automatically.

---

## 🔐 OAuth Flow

This project uses the **OAuth 2.0 installed application flow** — the Google-recommended approach for local scripts.

1. Script starts a local server via `flow.run_local_server()`
2. Google presents a consent screen
3. User grants permissions once
4. Script receives an authorization code, exchanges it for an access token + refresh token
5. Tokens are cached — no re-login on subsequent runs

---

## 🔁 Duplicate Prevention

Each email has a unique `msg_id`. After processing, the script persists it to `state.json`:

```json
{ "last_processed_id": "19b2b5e0d8ffb912" }
```

On the next run, any email matching the saved ID is skipped. This approach requires no database and works completely offline.

---

## 🧠 Edge Cases Handled

**Problem:** Google Sheets rejects cell values over 50,000 characters. Marketing emails with large HTML bodies triggered this error.

**Solution:** Truncation logic in `email_parser.py`:
```python
if len(body) > 50000:
    body = body[:50000] + " ...[TRUNCATED]"
```

The pipeline never crashes — metadata is always preserved even when body content is trimmed.

---

## 🚀 Automated Scheduling (GitHub Actions)

The script can run automatically on a schedule using GitHub Actions. Add this file to your repo:

`.github/workflows/run.yml`

```yaml
name: Gmail to Sheets Sync

on:
  schedule:
    - cron: '0 * * * *'   # runs every hour
  workflow_dispatch:        # also allows manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run sync
        env:
          GMAIL_TOKEN: ${{ secrets.GMAIL_TOKEN }}
          SHEETS_TOKEN: ${{ secrets.SHEETS_TOKEN }}
        run: python -m src.main
```

> Store your OAuth tokens as GitHub Secrets to avoid re-authorization in CI.

---

## ⚠️ Known Limitations

| Limitation | Detail |
|---|---|
| OAuth flow | Uses installed-app flow, not a service account. One-time manual auth required. |
| State tracking | Only the last processed email ID is persisted — not a full history. |
| Unread-only | Emails already marked as read before the script runs will be skipped. |
| HTML emails | Bodies exceeding 50k chars are truncated. Complex HTML may lose some formatting. |

---

## 📌 Potential Improvements

- Filter emails by subject keyword or sender domain
- Extract and log Gmail labels
- Skip `no-reply` addresses automatically
- Process only emails from the last N hours
- Add retry logic for network failures
- Dockerize for portable deployment

---

## 🛠️ Tech Stack

`Python` · `Gmail API` · `Google Sheets API` · `OAuth 2.0` · `GitHub Actions`

---

## 👨‍💻 Author

**Thushank Sachin Bagal**  
[LinkedIn](https://linkedin.com/in/thushankbagal) · [GitHub](https://github.com/thushanksachin10)
