import requests
from datetime import datetime, timedelta

# Define the necessary variables
client_id = '605ca15b-8466-40c1-92f0-681179d37409'
client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
user_email = 'sajal@payrollcloudcorp.com'  # Ensure this is the correct UPN

# Function to get access token from Azure AD
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
    token = response.json().get('access_token', None)
    if token:
        return token
    else:
        raise Exception("Failed to retrieve access token")

# Function to create an event with a Teams meeting link and retrieve the event URL
def create_event_with_teams_link():
    access_token = get_access_token()

    # Debugging: Print the access token
    print(f'Access Token: {access_token}')
    if not access_token:
        print("Failed to retrieve access token")
        return None

    # Prepare data for creating an event with a Teams meeting link
    url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'subject': 'Test Event with Teams Meeting',
        'body': {
            'contentType': 'HTML',
            'content': 'This is a test event with a Teams meeting link.'
        },
        'start': {
            'dateTime': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': (datetime.now() + timedelta(minutes=60)).isoformat(),
            'timeZone': 'UTC'
        },
        'attendees': [
            {
                'emailAddress': {
                    'address': user_email,
                    'name': 'Sajal'
                },
                'type': 'required'
            }
        ],
        'isOnlineMeeting': True,
        'onlineMeetingProvider': 'teamsForBusiness'
    }

    # Debugging: Print URL, headers, and payload
    print(f'URL: {url}')
    print(f'Headers: {headers}')
    print(f'Payload: {data}')

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        event = response.json()
        print('event', event)

        if 'webLink' in event:
            return event['webLink']
        else:
            print('Event URL not found in response.')
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        print(f'Response status code: {response.status_code}')
        print(f'Response content: {response.content.decode()}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

# Main execution
if __name__ == '__main__':
    event_url = create_event_with_teams_link()
    if event_url:
        print(f'Event URL: {event_url}')
    else:
        print('Failed to generate event URL.')
