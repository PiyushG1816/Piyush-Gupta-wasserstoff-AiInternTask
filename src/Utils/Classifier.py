def classify_email(subject, body):
    text = f"{subject.lower()} {body.lower()}"
    if any(keyword in text for keyword in ["invoice", "payment", "salary", "bank", "finance"]):
        return "Finance"
    elif any(keyword in text for keyword in ["flight", "hotel", "booking", "reservation", "travel"]):
        return "Travel"
    elif any(keyword in text for keyword in ["meeting", "schedule", "call", "appointment"]):
        return "Meetings"
    else:
        return "General"