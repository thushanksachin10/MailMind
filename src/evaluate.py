import pickle
from googleapiclient.discovery import build
from config import SHEET_ID

creds = pickle.load(open('token_sheets.pickle', 'rb'))
service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range='Sheet1!A:H'
).execute()
rows = result.get('values', [])

total = len(rows)
categories = {}
priorities = {}
confidence_scores = []

for row in rows[1:]:
    if len(row) >= 8:
        category = row[4] if len(row) > 4 else 'Unknown'
        priority = row[6] if len(row) > 6 else 'Unknown'
        confidence = float(row[7]) if len(row) > 7 else 0.0
        categories[category] = categories.get(category, 0) + 1
        priorities[priority] = priorities.get(priority, 0) + 1
        confidence_scores.append(confidence)

avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

print(f'Total emails processed: {total}')
print(f'Average confidence score: {avg_confidence:.2f}')
print(f'Category breakdown: {categories}')
print(f'Priority breakdown: {priorities}')