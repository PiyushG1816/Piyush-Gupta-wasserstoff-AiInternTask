from src.Database.Email_storage import fetch_emails_with_attachments
from src.utils.Summarizer import summarize_email
from src.services.Web_search import web_search

def should_trigger_search(email_body,subject):
    question_keywords = ["what is", "how to", "who is", "where is", "when is", "define", "explain"]
    email_body_lower = email_body.lower()
    return any(keyword in email_body_lower for keyword in question_keywords)

def handle_email_with_search(body, subject):
    text = subject if len(body.split()) < 30 or len(body.split()) > 1024 else body
    query = text.split(".")[0][:100]
    web_info = web_search(query)
    return f"I found the following information:\n\n{web_info}"

emails = fetch_emails_with_attachments()

for email in emails:
    email_body = email['body']
    subject= email["subject"]
    reply = handle_email_with_search(email_body,subject)
    print("Reply draft:\n", reply)