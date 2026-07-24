import json
import requests
from config import OPENROUTER_API_KEY
import re

def extract_important_links(body):
    links = re.findall(r'https?://[^\s<>"]+', body)
    keywords = ['interview', 'assessment', 'offer', 'apply', 
                'zoom', 'meet', 'calendar', 'hackerrank', 
                'codility', 'test', 'schedule']
    return [l for l in links if any(k in l.lower() for k in keywords)][:5]

def clean_body(body):
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'\s+', ' ', body).strip()
    return body[:1500]

def classify_email(subject, sender, body):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    cleaned_body = clean_body(body)
    important_links = extract_important_links(body)

    prompt = f"""
    You are an email classifier for a job seeker.
    Analyze the following email and return ONLY valid JSON.

    The JSON must have exactly these fields:
    {{
    "category": "",
    "summary": "",
    "priority": "",
    "confidence": 0.0
    }}

    Rules:
    - category must be one of:
    * Interview - interview scheduled, invite, or   confirmation
    * Assessment - coding test, assignment, or online test link
    * Offer - job offer or salary discussion
    * Rejection - application rejected
    * Application - application received or under review
    * Networking - recruiter reaching out or LinkedIn connection
    * Finance - payments, invoices, bank emails
    * Spam - promotions, newsletters, unrelated marketing
    * Other - anything else

    - priority rules (be strict):
    * HIGH: Interview, Assessment, Offer — these need immediate action
    * MEDIUM: Networking, Application updates
    * LOW: Rejection, Finance, Spam, Other

    - summary: one sentence max 20 words, focus on action needed
    - confidence: number between 0 and 1

    Email:
    Subject: {subject}
    Sender: {sender}
    Sender Domain: {sender.split('@')[-1]}
    Body Preview: {cleaned_body}
    Important Links: {important_links if important_links else 'None'}
    """

    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Classification failed: {e}")
        return {
            "category": "Other",
            "summary": "Unable to classify email.",
            "priority": "low",
            "confidence": 0.0
        }