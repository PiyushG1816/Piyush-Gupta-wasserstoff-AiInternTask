from transformers import pipeline
from src.Database.Email_storage import connect_db,fetch_emails_with_attachments

# Load the model only once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_email(text, subject, min_words=30, max_words=1024):
    """Summarizes email content using Hugging Face Transformers, only if the email is long."""

    words = text.split()
    word_count = len(words)
    try:
        if word_count < min_words or word_count > max_words:
            return subject  # Use subject for short or overly long emails

        # Truncate text to max_words for safety
        else:
            text = ' '.join(words[:max_words])

            summary = summarizer(
                text,
                max_length=100,
                min_length=30,
                do_sample=False
            )
            return summary[0]['summary_text']
        
    except Exception as e:
        return subject

def email_exists(message_id, cursor):
    """Check if an email with the given message_id already exists in the database."""
    query = "SELECT COUNT(*) FROM emails WHERE message_id = %s"
    cursor.execute(query, (message_id,))
    result = cursor.fetchone()
    return result[0] > 0

def store_email_with_summary(email_data):
    db, cursor = connect_db()
    """Stores email (original + summarized) in MySQL, avoiding duplicates."""
    query = """
        INSERT INTO emails (message_id, sender, recipient, subject, timestamp, body, summary, has_attachment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            subject = VALUES(subject),
            body = VALUES(body),
            timestamp = VALUES(timestamp),
            has_attachment = VALUES(has_attachment),
            summary = VALUES(summary)
    """
    cursor.execute(query, email_data)
    db.commit()

# Fetch and process emails
emails = fetch_emails_with_attachments()

if not emails:
    print("No emails fetched!")
else:
    for email in emails:
        summarized_body = summarize_email(email["body"],email["subject"])

        email_data = (
            email["id"],
            email["sender"],
            email["recipient"],
            email["subject"],
            email["timestamp"],
            email["body"],
            summarized_body,
            email["has_attachment"]
        )
        store_email_with_summary(email_data)
    print("Emails fetched, summarized, and stored!")
