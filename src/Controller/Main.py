from src.Database.Email_storage import fetch_emails_with_attachments
from src.utils.Summarizer import summarize_email
from src.services.Slack_services import send_slack_message,is_important_email
from src.utils.Search import should_trigger_search,handle_email_with_search
from src.services.Calender_services import appointment
from src.services.Reply_services import generate_reply, send_email_reply
from src.utils.Classifier import classify_email
from googleapiclient.errors import HttpError

def Personal_email_assistant():
    total_replies_attempted = 0
    replies_sent = 0
    replies_skipped = 0

    emails = fetch_emails_with_attachments()

    for email in emails:
        total_replies_attempted += 1

        summary = summarize_email(email["body"],email["subject"])
        email["summary"] = summary

        label = classify_email(email["subject"], email["body"])  # <--- NEW
        
        reply_body = f"Here is a quick summary of your email:\n\n{summary}"

        if should_trigger_search(email["body"], email["subject"]):
            reply_body = handle_email_with_search(summary)
            
        elif "schedule" in summary.lower() or "meeting" in summary.lower():
            meeting_details = appointment(summary)
            if meeting_details:
                reply_body = generate_reply(email["body"], meeting_details)
            else:
                reply_body = "I couldn't extract the meeting details. Could you please confirm the time and date?"

        try:    
            send_email_reply(
            to_email=email["sender"],
            subject=email["subject"],
            message_text=reply_body,
            thread_id=email["id"]
            )
            replies_sent += 1

        except HttpError as error:
            if error.resp.status == 404:
                replies_skipped += 1
                print("Skipped: Email does not exist or was deleted.")
            else:
                print("An error occurred while sending reply:", error)

        if is_important_email(email["subject"], email["sender"], email["body"]):
            slack_message = (
                f"📩 *New Email* [{label}]\n"
                f"*Subject:* {email['subject']}\n"
                f"*From:* {email['sender']}"
            )
            send_slack_message(slack_message)

        print(f"Email labeled as: {label}")

    # Final report
    print("\n=== Reply Summary ===")
    print(f"Total replies attempted: {total_replies_attempted}")
    print(f"Replies sent: {replies_sent}")
    print(f"Skipped due to missing/deleted emails: {replies_skipped}")

    return "All work is done."

if __name__ == "__main__":
    Personal_email_assistant()