# Personal Email Assistant

A smart AI-powered assistant that integrates with your Gmail inbox, understands email context using LLMs, and takes automated actions like replying, scheduling calendar events, performing web searches, and sending notifications via Slack.

---

## Overview

This assistant reads emails from your Gmail inbox, summarizes them using a large language model (LLM), classifies their intent, and then takes appropriate actions such as:
- Generating and sending contextual replies
- Extracting and scheduling meetings on Google Calendar
- Searching the web when necessary
- Sending alerts for important emails via Slack

It also stores all email data in a local MySQL database for persistent context and analysis.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Personal-Email-Assistant.git
cd Personal-Email-Assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Credentials

#### Gmail API
- Go to https://console.cloud.google.com/
- Create a project and enable the **Gmail API** and **Google Calendar API**
- Configure OAuth2 consent screen
- Download the `credentials.json` and place it in the root directory

#### Google Custom Search API
- Go to https://programmablesearchengine.google.com/
- Create a custom search engine and get the `cx` and `API key`
- Add them to your `.env`:
```env
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id
```

#### Slack Webhook
- Create a bot in your Slack workspace and generate a bot token
- Add the token to `.env`:
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=channel_id_here
```

---

## How It Works

### 1. Email Fetching
- Uses the Gmail API with OAuth2 to fetch the latest emails from the inbox.
- Parses key fields: sender, subject, body, attachments, timestamp, thread ID.
- Stores new emails in a MySQL database and avoids duplicates.

### 2. Summarization (LLM Integration)
- The email body and subject are passed to a Hugging Face model (e.g., `facebook/bart-large-cnn`) to generate a concise summary.

### 3. Classification
- The summary and content are passed through a classifier (custom or fine-tuned) to label the email intent (e.g., "Meeting Request", "Support Query", etc.).

### 4. Action Routing
- **Search:** If the email suggests a query, Google Custom Search is triggered.
- **Calendar:** If it mentions scheduling, the assistant extracts time/location and creates a Google Calendar event.
- **Reply:** Generates a polite, context-aware reply and sends it using Gmail API.
- **Slack Notification:** For high-importance emails, alerts are sent to a Slack channel.

---

## Running the Assistant

```bash
python Assistant.py
```

The script will:
- Authenticate Gmail & fetch new emails
- Summarize and classify each email
- Perform actions (search, calendar, reply, Slack)
- Log outputs in terminal

---

## Architecture Diagram

You can generate your own using [draw.io](https://draw.io) or tools like Excalidraw.

```
+-------------+     +--------------+     +----------------+     +--------------+
| Gmail Inbox | --> | Fetch Emails | --> |   Summarizer   | --> | Classifier   |
+-------------+     +--------------+     +----------------+     +--------------+
                                                               |
                                                               v
                                                   +------------------------+
                                                   | Action Decision Engine |
                                                   +------------------------+
                                                      |    |       |       |
                                                      v    v       v       v
                                               +--------+ +-------+ +---------+
                                               | Search | | Reply | | Calendar|
                                               +--------+ +-------+ +---------+
                                                      |
                                                      v
                                                +-------------+
                                                | Slack Alert |
                                                +-------------+
```

---

## Database Schema

- `emails` table stores:
  - `id`, `sender`, `recipient`, `subject`, `body`, `summary`, `timestamp`, `thread_id`, `label`, `has_attachment`

---

## Example Output

Email:
```
Subject: Meeting Request
Body: Can we schedule a call to discuss the Q2 roadmap?
```

Summary:
> "Request to schedule a meeting to discuss the Q2 roadmap."

Classification:
> "Meeting Request"

Actions:
- Extracts meeting intent
- Schedules event via Google Calendar
- Sends polite confirmation reply

---

## ❗ Troubleshooting

- **429 Error from Google API:** Quota exceeded; retry after 1:30 PM IST
- **OAuth Token Expired:** Delete `token.json` and re-authenticate
- **No Emails Fetched:** Check Gmail API scopes or inbox filters

---

## 📌 Future Improvements
- Web UI to visualize email summaries and actions
- Support for attachments and PDF parsing
- Enhanced LLM prompt tuning for specific domains



