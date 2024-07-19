import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import json

# # MongoDB connection
# client = MongoClient('your_mongo_db_connection_string')
# db = client.your_database
# collection = db.your_collection

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

# # Function to fetch data from MongoDB
# def fetch_data():
#     return list(collection.find({}))

# Function to fetch Teams data
def fetch_teams_data(access_token, user_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/joinedTeams'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to fetch Outlook calendar events
def fetch_calendar_events(access_token, user_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to fetch Outlook emails
def fetch_emails(access_token, user_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to print event details in a systematic format
def print_event_details(event):
    print(f"Subject: {event['subject']}")
    print(f"Start Time: {event['start']['dateTime']} ({event['start']['timeZone']})")
    print(f"End Time: {event['end']['dateTime']} ({event['end']['timeZone']})")
    print(f"Location: {event.get('location', {}).get('displayName', 'N/A')}")
    print(f"Organizer: {event['organizer']['emailAddress']['name']} ({event['organizer']['emailAddress']['address']})")
    
    # Print attendees if they exist
    if event.get('attendees'):
        print("Attendees:")
        for attendee in event['attendees']:
            print(f"  - {attendee['emailAddress']['name']} ({attendee['emailAddress']['address']})")
    else:
        print("Attendees: None")
    
    # Print join URL if available, otherwise mark as N/A
    online_meeting = event.get('onlineMeeting')
    join_url = online_meeting.get('joinUrl') if online_meeting else 'N/A'
    print(f"Join URL: {join_url}")
    
    # Print body preview if available
    print(f"Body Preview: {event['bodyPreview']}")
    print("="*50)

# Main script
if __name__ == "__main__":
    # Your Azure AD details
    client_id = '605ca15b-8466-40c1-92f0-681179d37409'
    client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
    tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
    user_id = 'sajal@payrollcloudcorp.com' # Change this to the user email or ID you want to target
    
    access_token = get_access_token(client_id, client_secret, tenant_id)
    # print('access_token',access_token)
    # data_from_db = fetch_data()
    
    teams_data = fetch_teams_data(access_token, user_id)
    calendar_events = fetch_calendar_events(access_token, user_id)
    emails = fetch_emails(access_token, user_id)
    
    # Process and display the fetched Teams data, calendar events, and emails
    # print("Teams Data:", teams_data)
    print("Calendar Events:")
    for event in calendar_events.get('value', []):
        print_event_details(event)
    # print("Emails:", emails)
    
    # for data in data_from_db:
    #     event_data = {
    #         'subject': data.get('subject', 'No Subject'),
    #         'start': {
    #             'dateTime': data.get('start_time', datetime.now().isoformat()),  # Default to current time if not provided
    #             'timeZone': 'UTC'
    #         },
    #         'end': {
    #             'dateTime': data.get('end_time', (datetime.now() + timedelta(hours=1)).isoformat()),  # Default to one hour from now if not provided
    #             'timeZone': 'UTC'
    #         }
    #     }
    #     create_event_for_user(access_token, user_id, event_data)
