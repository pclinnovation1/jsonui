import requests
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

# MongoDB connection
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
collection = db['Session_details']

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

# Function to create an online meeting
def create_online_meeting(access_token, user_id, subject, start_time, end_time):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings'
    print("url",url)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    meeting_data = {
        "startDateTime": start_time,
        "endDateTime": end_time,
        "subject": subject
    }
    response = requests.post(url, headers=headers, json=meeting_data)
    print("respo",response)
    return response.json().get('joinUrl')

# Function to create calendar event with Teams meeting link
def create_event_for_user(access_token, user_id, event_data, meeting_link):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    event_data['onlineMeetingUrl'] = meeting_link
    response = requests.post(url, headers=headers, json=event_data)
    return response.json()

# Function to generate dates based on recurrence pattern
def generate_recurrence_dates(start_time, repeat, end_on=None):
    dates = []
    current_date = start_time
    end_date = datetime.fromisoformat(end_on.replace('Z', '+00:00')) if end_on else None
    
    while True:
        if end_date and current_date > end_date:
            break
        dates.append(current_date)
        if repeat == "Daily":
            current_date += timedelta(days=1)
        elif repeat == "Weekly":
            current_date += timedelta(weeks=1)
        elif repeat == "Monthly":
            current_date = current_date.replace(month=current_date.month + 1)
        else:
            break
    return dates

# Function to process and store session details in MongoDB and create calendar events
def process_sessions(data):
    client_id = '605ca15b-8466-40c1-92f0-681179d37409'
    client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
    tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
    
    access_token = get_access_token(client_id, client_secret, tenant_id)
    instructor_email = data['session_details']['instructor_email']
    learner_emails = data['session_details']['learner_emails']
    
    for activity in data['session_details']['activity_details']:
        start_time = datetime.fromisoformat(activity['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(activity['end_time'].replace('Z', '+00:00'))
        subject = activity['subject']
        repeat = activity.get('repeat', 'None')
        end_on = activity.get('end_on')
        
        recurrence_dates = generate_recurrence_dates(start_time, repeat, end_on)
        
        for start_date in recurrence_dates:
            end_date = start_date + (end_time - start_time)
            start_date_str = start_date.isoformat()
            end_date_str = end_date.isoformat()
            
            # Create the online meeting and get the meeting link
            meeting_info = create_online_meeting(access_token, instructor_email, subject, start_date_str, end_date_str)
            meeting_link = meeting_info.get('joinUrl')
            print("link",meeting_link)
            
            # Create the event for the instructor
            event_data = {
                'subject': subject,
                'start': {'dateTime': start_date_str, 'timeZone': 'UTC'},
                'end': {'dateTime': end_date_str, 'timeZone': 'UTC'}
            }
            create_event_for_user(access_token, instructor_email, event_data, meeting_link)
            
            # Create the event for each learner
            for learner_email in learner_emails:
                create_event_for_user(access_token, learner_email, event_data, meeting_link)
            
            # Store the session details in MongoDB
            session_entry = {
                'subject': subject,
                'start_time': start_date_str,
                'end_time': end_date_str,
                'meeting_link': meeting_link,
                'instructor_email': instructor_email,
                'learner_emails': learner_emails
            }
            collection.insert_one(session_entry)

# Example JSON input
json_input = {
    "session_details": {
        "title": "New Course for testing 2.0",
        "activity_details": [
            {
                "subject": "Session 1",
                "start_time": "2024-07-01T09:00:00Z",
                "end_time": "2024-07-01T11:00:00Z",
                "repeat": "None"
            },
            {
                "subject": "Session 2",
                "start_time": "2024-07-02T09:00:00Z",
                "end_time": "2024-07-02T11:00:00Z",
                "repeat": "Daily",
                "end_on": "2024-07-07T11:00:00Z"
            }
        ],
        "instructor_email": 'sajal@payrollcloudcorp.com',
        "learner_emails": [
            "learner1@example.com",
            "learner2@example.com"
        ]
    }
}

# Process the input
process_sessions(json_input)
