import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import json

# MongoDB connection details
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
collection = db['Calendar_Details_From_Teams']

# Function to get access token
def get_access_token(client_id, client_secret, tenant_id):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token')

# Function to fetch Outlook calendar events for a specific period with pagination
def fetch_calendar_events(access_token, user_id, start_datetime, end_datetime):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/calendarView'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'startDateTime': start_datetime.isoformat(),
        'endDateTime': end_datetime.isoformat(),
        '$top': 100  # Increase the number of records per page
    }
    
    events = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        events.extend(data.get('value', []))
        url = data.get('@odata.nextLink')  # Get the next page URL if available
        params = None  # Reset params for subsequent requests

    return events

# Function to store event in MongoDB collection
def store_event_in_mongodb(event):
    # Check if event exists in MongoDB collection
    existing_event = collection.find_one({'event_id': event['event_id']})

    if existing_event:
        # Update existing event
        result = collection.update_one({'event_id': event['event_id']}, {'$set': event})
        print(f"Updated event with event_id {event['event_id']}. Matched: {result.matched_count}, Modified: {result.modified_count}")
    else:
        # Insert new event
        result = collection.insert_one(event)
        print(f"Inserted new event with event_id {event['event_id']}. Inserted ID: {result.inserted_id}")

# Function to print event details in a systematic format
def print_event_details(event):
    print("="*50)
    print(f"Subject: {event.get('subject', 'N/A')}")
    print(f"Start Time: {event['start'].get('dateTime', 'N/A')} ({event['start'].get('timeZone', 'N/A')})")
    print(f"End Time: {event['end'].get('dateTime', 'N/A')} ({event['end'].get('timeZone', 'N/A')})")
    print(f"Location: {event.get('location', {}).get('displayName', 'N/A')}")
    
    organizer_name = event['organizer']['emailAddress'].get('name', 'N/A') if 'organizer' in event else 'N/A'
    organizer_address = event['organizer']['emailAddress'].get('address', 'N/A') if 'organizer' in event else 'N/A'
    print(f"Organizer: {organizer_name} ({organizer_address})")
    
    attendees = event.get('attendees', [])
    if attendees:
        print("Attendees:")
        for attendee in attendees:
            attendee_name = attendee['emailAddress'].get('name', 'N/A') if 'emailAddress' in attendee else 'N/A'
            attendee_address = attendee['emailAddress'].get('address', 'N/A') if 'emailAddress' in attendee else 'N/A'
            print(f"  - {attendee_name} ({attendee_address})")
    else:
        print("Attendees: None")
    
    online_meeting = event.get('onlineMeeting')
    if online_meeting and online_meeting.get('joinUrl'):
        print(f"Join URL: {online_meeting['joinUrl']}")
    else:
        print("Join URL: Not specified")
    
    print(f"Body Preview: {event.get('bodyPreview', 'N/A')}")
    print("="*50)

# Main script
if __name__ == "__main__":
    # Your Azure AD details
    client_id = '605ca15b-8466-40c1-92f0-681179d37409'
    client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
    tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
    user_id = 'dan@payrollcloudcorp.com'  # Change this to the user email or ID you want to target
    
    access_token = get_access_token(client_id, client_secret, tenant_id)
    
    # # Define the time range for fetching events (past 15 days and next 15 days)
    # start_datetime = datetime.utcnow() - timedelta(days=15)
    # end_datetime = datetime.utcnow() + timedelta(days=15)

    # Define the specific date range for July 30, 2024
    start_datetime = datetime(2024, 7, 15)
    end_datetime = datetime(2024, 7, 16) - timedelta(seconds=1)  # T
    
    # Fetch calendar events for the specified period
    calendar_events = fetch_calendar_events(access_token, user_id, start_datetime, end_datetime)
    
    # Connect to MongoDB and store events
    if calendar_events:
        for event in calendar_events:
            if event is None:
                continue  # Skip processing None events
            
            # Safe access with try-except block
            try:
                join_url = event.get('onlineMeeting', {}).get('joinUrl', 'Not specified')
            except AttributeError as e:
                print(f"Error accessing joinUrl for event: {event}. Error: {e}")
                join_url = 'Not specified'
            
            event_data = {
                'event_id': event['id'],
                'subject': event.get('subject', 'N/A'),
                'start': {
                    'dateTime': event['start'].get('dateTime', 'N/A'),
                    'timeZone': event['start'].get('timeZone', 'N/A')
                },
                'end': {
                    'dateTime': event['end'].get('dateTime', 'N/A'),
                    'timeZone': event['end'].get('timeZone', 'N/A')
                },
                'location': event.get('location', {}).get('displayName', 'N/A'),
                'organizer': event.get('organizer', {}).get('emailAddress', {}).get('address', 'N/A'),
                'attendees': [attendee['emailAddress'].get('address', 'N/A') for attendee in event.get('attendees', [])],
                'join_url': join_url,
                'body_preview': event.get('bodyPreview', 'N/A')
            }
            store_event_in_mongodb(event_data)
    
    # Optionally print fetched events
    print("Fetched Calendar Events:")
    for event in calendar_events:
        print_event_details(event)