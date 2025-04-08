import mysql.connector
import os
import base64
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from bs4 import BeautifulSoup
import pickle

ATTACHMENTS_DIR = "attachments"

def connect_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="Email_assistant"
    )
    return db, db.cursor()

def store_email(data):
    db, cursor = connect_db()

    query = """
        INSERT INTO emails (
            message_id, sender, recipient, subject, timestamp, body, has_attachment,thread_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            sender = VALUES(sender),
            recipient = VALUES(recipient),
            subject = VALUES(subject),
            timestamp = VALUES(timestamp),
            body = VALUES(body),
            has_attachment = VALUES(has_attachment),
            thread_id = VALUES(thread_id)
    """
    cursor.execute(query, data)
    db.commit()
    cursor.close()
    db.close()

def extract_email_address(recipient_str):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', recipient_str)
    return emails[0] if emails else recipient_str

def extract_body(payload):
    def extract_parts(parts):
        plain_text = ""
        html_text = ""

        for part in parts:
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data")

            if mime_type == "multipart/alternative" and "parts" in part:
                # Nested parts — handle recursively
                nested_plain, nested_html = extract_parts(part["parts"])
                if nested_plain:
                    plain_text = nested_plain
                elif nested_html:
                    html_text = nested_html

            elif body_data:
                decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
                if mime_type == "text/plain":
                    plain_text = decoded
                elif mime_type == "text/html":
                    html_text = decoded

        return plain_text, html_text

    def clean_html(html):
        soup = BeautifulSoup(html, "html.parser")
        if soup.body:
            return soup.body.get_text(separator="\n", strip=True)
        else:
            return soup.get_text(separator="\n", strip=True)

    if "parts" in payload:
        plain, html = extract_parts(payload["parts"])
        if plain:
            return plain
        elif html:
            return clean_html(html)
    elif "body" in payload and "data" in payload["body"]:
        decoded = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        return clean_html(decoded)

    return ""

def store_attachment(email_id, filename, file_path):
    db, cursor = connect_db()
    query = "INSERT INTO attachments (email_id, filename, file_path) VALUES (%s, %s, %s)"
    cursor.execute(query, (email_id, filename, file_path))
    db.commit()
    cursor.close()
    db.close()

def attachments(service, msg_data, email_id):
    parts = msg_data.get("payload", {}).get("parts", [])
    for part in parts:
        if part.get("filename"):  # Attachment exists
            return "Yes"
    return "No"

def fetch_emails_with_attachments():
    with open("token.pickle", "rb") as f:
        creds = pickle.load(f)

    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    email_list = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        message_id = msg_data["id"]
        thread_id = msg_data.get("threadId")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        recipient_raw = next((h["value"] for h in headers if h["name"] == "To"), "Unknown")
        recipient = extract_email_address(recipient_raw)        
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        timestamp = datetime.utcfromtimestamp(int(msg_data["internalDate"]) / 1000)

        body = extract_body(msg_data["payload"])

        has_attachment = attachments(service, msg_data, message_id)
        attachment_status = "Yes" if has_attachment else "No"

        store_email((message_id, sender, recipient, subject, timestamp, body,  has_attachment, thread_id))

        # Add to list for further use
        email_list.append({
            "id": message_id,
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "timestamp": timestamp,
            "body": body,
            "has_attachment": has_attachment
        })

    return email_list

