from src.utils.Meeting_info import extract_meeting_info, parse_meeting_details
from googleapiclient.discovery import build
import pickle

def create_calendar_event(event_details):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
    service = build("calendar", "v3", credentials=creds)

    event = {
        'summary': event_details['summary'],
        'start': {'dateTime': event_details['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': event_details['end'], 'timeZone': 'UTC'}
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {created_event.get('htmlLink')}")

def appointment(email_body):
    info_str = extract_meeting_info(email_body)
    print("LLM Output:", info_str)
    details = parse_meeting_details(info_str)
    if details:
        create_calendar_event(details)
    else:
        print("Failed to extract meeting details.")
