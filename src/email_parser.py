import base64
from bs4 import BeautifulSoup

def parse_email(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg['payload']
    headers = payload['headers']

    sender = next(h['value'] for h in headers if h['name'] == 'From')
    subject = next(h['value'] for h in headers if h['name'] == 'Subject')
    date = next(h['value'] for h in headers if h['name'] == 'Date')

    body = ""
    if 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    else:
        for part in payload.get('parts', []):
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

    # Optional HTML to text conversion
    try:
        body = BeautifulSoup(body, 'html.parser').get_text()
    except:
        pass

    return sender, subject, date, body
