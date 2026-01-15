from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup

def parse_email(service, msg_id):
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = msg["payload"]["headers"]

    sender = subject = date = ""

    for header in headers:
        if header["name"] == "From":
            sender = header["value"]
        elif header["name"] == "Subject":
            subject = header["value"]
        elif header["name"] == "Date":
            date = header["value"]

    
    body = extract_body(msg["payload"])

    return sender, subject, date, body


def extract_body(payload):
    """Safely extract email body from multipart or single-part messages."""

    
    if "body" in payload and "data" in payload["body"]:
        data = payload["body"]["data"]
        return decode_data(data)

    
    if "parts" in payload:
        for part in payload["parts"]:
            # Look for plain text
            if part["mimeType"] == "text/plain":
                return decode_data(part["body"]["data"])

            # Look for HTML
            if part["mimeType"] == "text/html":
                html = decode_data(part["body"]["data"])
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text()

            # Nested parts
            if "parts" in part:
                result = extract_body(part)
                if result:
                    return result

    return "(No body found)"


def decode_data(data):
    decoded_bytes = urlsafe_b64decode(data)
    return decoded_bytes.decode("utf-8", errors="ignore")
