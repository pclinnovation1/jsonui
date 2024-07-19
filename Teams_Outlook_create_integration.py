import requests
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
collection = db['Calendar_Details']

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

# Function to fetch data from MongoDB
def fetch_data():
    return list(collection.find({}))

# Function to create calendar event for a specific user
def create_event_for_user(access_token, user_id, event_data):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=event_data)
    return response.json()

# Main script
if __name__ == "__main__":
    # Your Azure AD details
    client_id = '605ca15b-8466-40c1-92f0-681179d37409'
    client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
    tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
    user_id = 'sajal@payrollcloudcorp.com' # Change this to the user email or ID you want to target
    
    access_token = get_access_token(client_id, client_secret, tenant_id)
    data_from_db = fetch_data()
    
    for data in data_from_db:
        event_data = {
            'subject': data.get('subject', 'No Subject'),
            'start': {
                'dateTime': data.get('start_time', datetime.now().isoformat()),  # Default to current time if not provided
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': data.get('end_time', (datetime.now() + timedelta(hours=1)).isoformat()),  # Default to one hour from now if not provided
                'timeZone': 'UTC'
            }
        }
        create_event_for_user(access_token, user_id, event_data)



# import requests
# from pymongo import MongoClient
# from datetime import datetime, timezone
# import pytz

# # MongoDB connection
# client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
# db = client['PCL_Interns']
# collection = db['Calendar_Details']

# # Function to get access token
# def get_access_token(client_id, client_secret, tenant_id):
#     url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'scope': 'https://graph.microsoft.com/.default'
#     }
#     response = requests.post(url, headers=headers, data=data)
#     return response.json().get('access_token')

# # Function to fetch data from MongoDB
# def fetch_data():
#     return list(collection.find({}))

# # Function to create calendar event for a specific user
# def create_event_for_user(access_token, user_id, event_data):
#     url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, json=event_data)
#     return response.json()

# # Convert UTC to IST
# def convert_to_ist(utc_time_str):
#     utc_time = datetime.fromisoformat(utc_time_str)
#     utc_time = utc_time.replace(tzinfo=timezone.utc)
#     ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
#     ist_time = utc_time.astimezone(ist_timezone)
#     return ist_time.isoformat()


# # Main script
# if __name__ == "__main__":
#     # Your Azure AD details
#     client_id = '605ca15b-8466-40c1-92f0-681179d37409'
#     client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
#     tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
#     user_id = 'sajal@payrollcloudcorp.com' # Change this to the user email or ID you want to target
    
#     access_token = get_access_token(client_id, client_secret, tenant_id)
#     data_from_db = fetch_data()
    
#     for data in data_from_db:
#         event_data = {
#             'subject': data.get('subject', 'No Subject'),
#             'start': {
#                 'dateTime': convert_to_ist(data['start_time']),
#                 'timeZone': 'Asia/Kolkata'  # Setting timezone to IST
#             },
#             'end': {
#                 'dateTime': convert_to_ist(data['end_time']),
#                 'timeZone': 'Asia/Kolkata'  # Setting timezone to IST
#             }
#         }
#         create_event_for_user(access_token, user_id, event_data)
