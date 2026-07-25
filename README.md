# Intelligent Email Triage System using LLM-based Information Extraction

![CI](https://github.com/thushanksachin10/gmail_to_sheets/actions/workflows/run.yml/badge.svg)

A fully automated pipeline that ingests unread Gmail messages, applies an LLM layer for structured information extraction and intent classification, persists results to Google Sheets, and delivers real-time priority notifications via Telegram — running hourly on GitHub Actions with zero human intervention.

📊 **[Live Research Dashboard](https://thushanksachin10.github.io/gmail_to_sheets)** — real-time pipeline metrics, category breakdown, and confidence distribution.

---

## Research Motivation

Email inboxes are high-noise, low-signal environments. For a job seeker receiving hundreds of emails per week, the cognitive overhead of manually triaging messages is significant. Rule-based filters (keyword matching, sender whitelisting) fail on natural language — they cannot infer intent, urgency, or context from unstructured text.

This project explores a core question:

> **Can a lightweight open-source LLM reliably classify email intent and extract structured information with sufficient precision to support automated triage — and where does it fail?**

This is not a chatbot. It is a structured information extraction pipeline with an evaluation framework built on top of real inbox data.

---

## System Architecture

```
+-----------------------------+
|        Gmail Inbox          |
+-------------+---------------+
              |
              | Gmail API — fetch unread messages
              v
  +------------------------+
  |   gmail_service.py     |   OAuth 2.0 installed-app flow
  +------------------------+   token cached as .pickle
              |
              | Raw email metadata + HTML body
              v
  +------------------------+
  |   email_parser.py      |   HTML → plain text (BeautifulSoup)
  +------------------------+   truncation at 49k chars
              |
              | Cleaned subject, sender, date, body
              v
  +------------------------+
  |   ai_classifier.py     |   LLM via OpenRouter API
  +------------------------+   Structured JSON output
              |
              | category, summary, priority, confidence
              v
       +------+--------+
       |               |
       v               v
+------------+   +------------------+
| sheets_    |   | notifier.py      |
| service.py |   | Telegram Bot API |
+------------+   +------------------+
       |               |
       v               v
  Google Sheets    Phone notification       
  (8 columns)      (HIGH priority only,
       |            with Gmail deep link)
       v
  +------------------------+
  | generate_dashboard.py  |   reads Sheet → docs/data.json
  +------------------------+
       |
       v
  GitHub Pages Dashboard (auto-updated hourly)
       |
       v
  +------------+
  | state.json |   deduplication via msg_id persistence
  +------------+
```

---

## LLM Classification Layer

### Model
`meta-llama/llama-3.1-8b-instruct` via OpenRouter API — chosen for strong instruction-following on structured output tasks at zero inference cost.

### Task
Given an unstructured email, the model returns:

```json
{
  "category": "Interview",
  "summary": "Technical interview scheduled for July 28 at 3PM IST",
  "priority": "HIGH",
  "confidence": 0.94
}
```

### Input Preprocessing

Raw HTML email bodies are poor LLM inputs. The pipeline preprocesses before classification:

```python
# Strip HTML tags
body = re.sub(r'<[^>]+>', ' ', body)
body = re.sub(r'\s+', ' ', body).strip()
body = body[:1500]  # first 1500 chars carry classification signal

# Extract job-relevant links buried anywhere in the email
keywords = ['interview', 'assessment', 'offer', 'apply',
            'zoom', 'meet', 'calendar', 'hackerrank', 'codility']
important_links = [l for l in all_links if any(k in l.lower() for k in keywords)]
```

The LLM receives: subject + sender domain + cleaned body preview + extracted links — not raw HTML.

### Classification Schema

| Category | Priority | Rationale |
|---|---|---|
| Interview | HIGH | Requires immediate calendar action |
| Assessment | HIGH | Time-bound coding test or assignment |
| Offer | HIGH | Salary negotiation or acceptance deadline |
| Rejection | LOW | No action required |
| Application | MEDIUM | Status update, no urgent action |
| Networking | MEDIUM | Recruiter outreach, follow-up optional |
| Finance | LOW | Transactional, non-urgent |
| Spam | LOW | Promotions, newsletters |
| Other | LOW | Unclassified |

### Why LLM over Rule-Based?

A rule-based system fails on emails like:

```
"Hey, saw your profile. We're building something 
and might need help. Are you free to chat this week?"
```

No keywords. No explicit intent. A keyword filter assigns this LOW or Spam.

The LLM infers recruiter outreach from conversational tone and context, correctly assigning MEDIUM/Networking with a summary like *"Recruiter interested in potential collaboration."*

This intent inference from unstructured natural language is the core GenAI contribution of this project.

---

## Notification Architecture

The notification layer is deliberately abstracted:

```python
# main.py only calls this — agnostic to provider
send_notification(subject, sender, summary, priority, msg_id)
```

`notifier.py` is the only file that changes when switching providers (Telegram → WhatsApp → Slack). This separation of concerns means the core pipeline is provider-independent.

**Currently implemented: Telegram Bot API**

Notification fires only on `priority == "HIGH"` — reducing alert fatigue. Each notification includes a direct Gmail deep link:

```
https://mail.google.com/mail/u/0/#inbox/{msg_id}
```

One tap opens the exact email. No inbox searching required.

---

## Preliminary Results

Pipeline has processed **182 emails** with AI classification applied. Full real-time metrics on the [live dashboard](https://thushanksachin10.github.io/gmail_to_sheets).

**Average model confidence: 0.75**

**Category distribution:**

| Category | Count | % |
|---|---|---|
| Application | 98 | 53.8% |
| Other | 24 | 13.2% |
| Spam | 20 | 11.0% |
| Finance | 13 | 7.1% |
| Networking | 10 | 5.5% |
| Interview | 6 | 3.3% |
| Assessment | 5 | 2.7% |
| Offer | 4 | 2.2% |
| Rejection | 1 | 0.5% |

**Priority distribution:**

| Priority | Count |
|---|---|
| HIGH | 14 |
| MEDIUM | 72 |
| LOW | 96 |

---

## Failure Mode Analysis

**1. Confidence calibration**

Average confidence of 0.75 after preprocessing improvements (up from 0.54 on raw HTML input). Whether this confidence correlates with actual classification accuracy is an open research question — the pipeline logs confidence for every email to enable a future calibration study.

**2. Conservative priority assignment**

72 emails classified MEDIUM vs 14 HIGH suggests the model errs on the side of caution. This is desirable for notification systems (low false positive rate) but may cause genuine high-priority emails to be missed.

**Observed failure patterns:**

| Failure Type | Root Cause |
|---|---|
| Informal recruiter email classified as Other | Ambiguous tone, no explicit job signal |
| Over-classification as Application | Broad catch-all for job-related emails |
| Low confidence on mixed-intent emails | Email covers multiple topics simultaneously |
| Hallucinated summary detail | LLM generation tendency, not grounded extraction |

**Core open question:** Does self-reported LLM confidence at 0.75 average actually correlate with classification accuracy? This pipeline is designed to collect the data to answer that.

---

## Edge Cases Handled

**Google Sheets 50k character cell limit**

HTML-heavy emails crashed the pipeline. Fixed with truncation:

```python
if len(body) > 49000:
    body = body[:49000] + " ... [TRUNCATED]"
```

**LLM API failure resilience**

Classification failures fall back gracefully — pipeline continues logging emails even when LLM is unavailable:

```python
except Exception as e:
    print(f"Classification failed: {e}")
    return {"category": "Other", "summary": "Unable to classify.", 
            "priority": "low", "confidence": 0.0}
```

**OAuth token expiry in CI**

Tokens are base64-encoded and stored as GitHub Secrets, decoded at runtime — eliminating re-authorization in headless CI.

---

## Automated Deployment

Runs every hour via GitHub Actions. Two jobs: `sync` (email pipeline + dashboard data generation) and `deploy` (GitHub Pages publish).

```yaml
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
```

✅ Verified working in CI.

---

## Setup

```bash
git clone https://github.com/thushanksachin10/gmail_to_sheets.git
cd gmail_to_sheets
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Copy `config.example.py` to `config.py` and fill in your values:

```python
SHEET_ID = "your_google_sheet_id"
SHEET_RANGE = "Sheet1!A:H"
OPENROUTER_API_KEY = "your_openrouter_api_key"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_telegram_chat_id"
```

Enable Gmail API and Google Sheets API in [Google Cloud Console](https://console.cloud.google.com/), download OAuth credentials to `credentials/credentials.json`, then:

```bash
python -m src.main
```

---

## Known Limitations

| Limitation | Detail |
|---|---|
| State tracking | Only last processed `msg_id` persisted — not full history |
| Unread-only | Pre-read emails are never processed |
| Single-user | OAuth installed-app flow, not multi-tenant |
| Confidence calibration | Not yet validated against ground truth labels |
| Context truncation | Emails truncated to 1500 chars — signal in long bodies may be lost |

---

## Research Extensions

Motivated directly by observed failure modes:

- **Confidence calibration study** — ground truth labeling of 200+ emails to measure correlation between model confidence and actual accuracy
- **Few-shot prompting** — providing labeled examples in-prompt to improve recall on ambiguous recruiter emails
- **Model comparison** — Llama 3.1 8B vs Mistral 7B vs Gemma 9B on the same corpus, measuring F1 per category
- **RAG-based personalization** — retrieval of past email interaction patterns to improve priority scoring
- **Agentic extension** — moving from classification to action: auto-draft replies, auto-schedule interviews by reading calendar availability

---

## Tech Stack

`Python` · `Gmail API` · `Google Sheets API` · `OAuth 2.0` · `OpenRouter` · `LLaMA 3.1 8B` · `Telegram Bot API` · `GitHub Actions` · `GitHub Pages` · `CI/CD`

---

## Author

**Thushank Sachin Bagal**

[LinkedIn](https://linkedin.com/in/thushankbagal) · [GitHub](https://github.com/thushanksachin10)
