import requests
import json
from datetime import datetime, timedelta

# Define the necessary variables
client_id = '605ca15b-8466-40c1-92f0-681179d37409'
client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
user_email = 'sajal@payrollcloudcorp.com'
access_token = None

# Get an access token from Azure AD
def get_access_token():
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

# Create a calendar event
def create_calendar_event():
    global access_token
    access_token = get_access_token()

    url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    event_data = {
        'subject': 'Oracle Learning Session',
        'body': {
            'contentType': 'HTML',
            'content': 'Details about the learning session.'
        },
        'start': {
            'dateTime': (datetime.now() + timedelta(days=1)).isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            'timeZone': 'UTC'
        },
        'location': {
            'displayName': 'Microsoft Teams'
        },
        'attendees': [
            {
                'emailAddress': {
                    'address': user_email,
                    'name': 'Instructor/Learner Name'
                },
                'type': 'required'
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(event_data))
    response.raise_for_status()
    return response.json()

# Execute the function to create an event
created_event = create_calendar_event()
print(f'Event created: {created_event["id"]}')
