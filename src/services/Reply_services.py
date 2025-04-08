from email.mime.text import MIMEText
from transformers import pipeline
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import pickle

extractor = pipeline("text2text-generation", model="google/flan-t5-base")

def send_email_reply(to_email, subject, message_text,message_id=None, thread_id=None):
    try:
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
        service = build("gmail", "v1", credentials=creds)

        # Check if the message exists (to avoid replying to deleted ones)
        if message_id:
            try:
                service.users().messages().get(userId="me", id=message_id).execute()
            except HttpError as error:
                if error.resp.status == 404:
                    print(f"Message ID {message_id} not found. Skipping reply.")
                    return
                else:
                    raise

        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}"
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        body = {'raw': raw}
        if thread_id:
            body['threadId'] = thread_id

        sent = service.users().messages().send(userId="me", body=body).execute()
        print("Reply sent. Message ID:", sent['id'])

    except HttpError as error:
        print("An error occurred while sending reply. Entity not found")

def generate_reply(email_body, meeting_details):
    prompt = f"""
You are a helpful email assistant.

The user received the following email:
\"\"\"
{email_body}
\"\"\"

The assistant successfully scheduled a meeting with these details:
Title: {meeting_details.get('title')}
Date: {meeting_details.get('date')}
Time: {meeting_details.get('time')}
Location: {meeting_details.get('location')}

Draft a polite, concise reply to confirm the meeting.
"""
    reply = extractor(prompt, max_length=256, do_sample=False)[0]['generated_text']
    return reply
