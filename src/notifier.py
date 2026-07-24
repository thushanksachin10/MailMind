import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_notification(subject, sender, summary, priority):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    priority_emoji = {
        "HIGH": "⚡",
        "MEDIUM": "⭐",
        "LOW" : "🔅"
    }
    emoji = priority_emoji.get(priority.upper(), "📧")

    message = (
        f"{emoji} {priority.capitalize()} Priority Email\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Summary: {summary}"
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

    