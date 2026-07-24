import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_notification(subject, sender, summary, priority, msg_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    priority_emoji = {
        "HIGH": "⚡",
        "MEDIUM": "⭐",
        "LOW" : "🔅"
    }
    emoji = priority_emoji.get(priority.upper(), "📧")

    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{msg_id}"


    message = (
        f"{emoji} {priority.capitalize()} Priority Email\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Summary: {summary}\n\n"
        f"📬 Open Email: {gmail_link}"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Notification failed: {e}")
        return None

    