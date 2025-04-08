import pickle
import requests
from googleapiclient.discovery import build

# Slack Bot Token and Channel
SLACK_TOKEN = ""  # Replace with your actual Slack bot token
SLACK_CHANNEL = "#general"  # Replace with your Slack channel name or ID

# Define what makes an email "important"
def is_important_email(subject, sender, body):
    keywords = ["urgent", "important", "asap", "action required"]
    vip_senders = ["boss@example.com", "ceo@example.com"]

    subject = subject.lower()
    body = body.lower()
    sender = sender.lower()

    if any(k in subject or k in body for k in keywords):
        return True
    if sender in vip_senders:
        return True
    return False

# Function to send message to Slack
def send_slack_message(text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": SLACK_CHANNEL,
        "text": text
    }
    response = requests.post(url, json=data, headers=headers)
    if not response.ok or not response.json().get("ok"):
        print("Failed to send Slack message:", response.text)
    else:
        print("Slack message sent successfully.")

# Function to fetch emails from Gmail
def check_and_notify_important_emails():
    with open("token.pickle", "rb") as f:
        creds = pickle.load(f)

    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"].get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        body = msg_data.get("snippet", "")

        if is_important_email(subject, sender, body):
            slack_text = f" *Important Email*\n*From:* {sender}\n*Subject:* {subject}\n\n{body}"
            send_slack_message(slack_text)

if __name__ == "__main__":
    check_and_notify_important_emails()
