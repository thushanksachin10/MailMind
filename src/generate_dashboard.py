import pickle
import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from config import SHEET_ID

def generate():
    creds = pickle.load(open('token_sheets.pickle', 'rb'))
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range='Sheet1!A:H'
    ).execute()
    rows = result.get('values', [])[1:]  # skip header

    total = len(rows)
    categories = {}
    priorities = {}
    confidence_scores = []
    daily_counts = {}

    for row in rows:
        if len(row) >= 8:
            category = row[4] if len(row) > 4 else 'Unknown'
            priority = row[6].upper() if len(row) > 6 else 'UNKNOWN'
            date = row[2] if len(row) > 2 else ''

            try:
                confidence = float(row[7])
            except:
                confidence = 0.0

            categories[category] = categories.get(category, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
            confidence_scores.append(confidence)

            # daily count
            try:
                day = date[:10]
                daily_counts[day] = daily_counts.get(day, 0) + 1
            except:
                pass

    avg_confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0

    # confidence distribution buckets
    buckets = {"0.0-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}
    for c in confidence_scores:
        if c < 0.3: buckets["0.0-0.3"] += 1
        elif c < 0.5: buckets["0.3-0.5"] += 1
        elif c < 0.7: buckets["0.5-0.7"] += 1
        elif c < 0.9: buckets["0.7-0.9"] += 1
        else: buckets["0.9-1.0"] += 1

    data = {
        "total": total,
        "avg_confidence": avg_confidence,
        "categories": categories,
        "priorities": priorities,
        "confidence_distribution": buckets,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M IST")
    }

    os.makedirs('docs', exist_ok=True)
    with open('docs/data.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Dashboard data generated: {total} emails, avg confidence {avg_confidence}")

if __name__ == "__main__":
    generate()