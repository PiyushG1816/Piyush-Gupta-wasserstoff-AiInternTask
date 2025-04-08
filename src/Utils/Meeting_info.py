from transformers import pipeline
import re
from datetime import datetime, timedelta

# Load the model for extracting structured info from email text
extractor = pipeline("text2text-generation", model="google/flan-t5-large")

def extract_meeting_info(email_body):
    prompt = (
        "Extract meeting details from the email below.\n"
        "Follow this format exactly:\n"
        "title: <title>, date: <YYYY-MM-DD>, time: <HH:MM>, duration: <minutes>\n\n"
        "Example:\n"
        "Email: Let's catch up on 2025-04-10 at 14:30 for 45 minutes to review the project.\n"
        "Output: title: Project Review, date: 2025-04-10, time: 14:30, duration: 45\n\n"
        f"Email: {email_body}\n"
        "Output:"
    )
    result = extractor(prompt, max_length=128, do_sample=False)
    return result[0]['generated_text']

def parse_meeting_details(info_str):
    pattern = r"title:\s*(.*?),\s*date:\s*(\d{4}-\d{2}-\d{2}),\s*time:\s*(\d{2}:\d{2}),\s*duration:\s*(\d+)"
    match = re.search(pattern, info_str)
    if not match:
        return None
    title, date_str, time_str, duration_str = match.groups()
    start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(minutes=int(duration_str))
    return {
        "summary": title,
        "start": start_time.isoformat(),
        "end": end_time.isoformat()
    }