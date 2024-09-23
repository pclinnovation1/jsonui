# from flask import Flask, request, jsonify
# from pymongo import MongoClient

# app = Flask(__name__)

# # MongoDB client setup (change URI accordingly)
# client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')
# db = client['oras']

# meetings_collection = db['PGM_talent_review_meeting']
# employees_collection = db['HRM_employee_details'] 

# potential_assessments_collection = db['PGM_potential_assessments']
# performance_assessments_collection = db['PGM_performance_assessments']
# talent_review_meeting_collection = db['PGM_talent_review_meeting']

# # Helper function to fetch the organization for the business leader
# def fetch_organization(business_leader):
#     employee = employees_collection.find_one({"person_name": business_leader})
#     if employee:
#         return employee.get("organization")
#     return None

# # Helper function to check if a participant is a manager
# def is_manager(participant):
#     manager = employees_collection.find_one({"person_name": participant})
#     if manager and manager.get('working_as_manager', 'No') == 'Yes':
#         return True
#     return False

# # Helper function to validate employees are reporting to one of the managers
# def validate_employees_with_managers(employees, managers):
#     valid_employees = []
#     for employee_name in employees:
#         employee = employees_collection.find_one({"person_name": employee_name})
#         if employee and employee.get('manager_name') in managers:
#             valid_employees.append(employee_name)
#         else:
#             print(f"Skipping employee {employee_name} as they are not reporting to any of the listed managers.")
#     return valid_employees

# # Create Meeting with custom logic
# @app.route('/create_meeting', methods=['POST'])
# def create_meeting():
#     data = request.json

#     # Fetch the organization for the business leader
#     business_leader = data['meeting_info'].get('business_leader')
#     organization = fetch_organization(business_leader)
#     if not organization:
#         return jsonify({"error": f"Business leader '{business_leader}' not found in employee details"}), 400
#     data['meeting_info']['organization'] = organization  # Adding the organization to the meeting info

#     # Set the default meeting status to "Not started"
#     data['meeting_info']['meeting_status'] = "Not started"

#     # Validate review participants (managers)
#     review_participants = data.get('review_participants', [])
#     for participant in review_participants:
#         if not is_manager(participant):
#             return jsonify({"error": f"Participant '{participant}' is not listed as a manager in employee details"}), 400

#     # Validate employees under population_selection
#     employees = data.get('population_selection', {}).get('employees', [])
#     valid_employees = validate_employees_with_managers(employees, review_participants)

#     if not valid_employees:
#         return jsonify({"error": "No valid employees found who report to the listed managers"}), 400
    
#     data['population_selection']['employees'] = valid_employees  # Updating valid employees only

#     # Fetch potential assessment by name
#     potential_assessment_name = data['review_content'].get('potential_assessment')
#     if potential_assessment_name:
#         potential_assessment = potential_assessments_collection.find_one({"assessment_name": potential_assessment_name})
#         if not potential_assessment:
#             return jsonify({"error": f"Potential assessment '{potential_assessment_name}' not found"}), 400
#         data['review_content']['potential_assessment'] = {
#             "assessment_name": potential_assessment.get('assessment_name'),
#             "questions": potential_assessment.get('questions')
#         }

#     # Fetch performance assessment by name
#     performance_assessment = data['review_content'].get('performance_assessment')
#     if performance_assessment:
#         performance_assessment = performance_assessments_collection.find_one({"assessment_name": performance_assessment})
#         if not performance_assessment:
#             return jsonify({"error": f"Performance assessment '{performance_assessment}' not found"}), 400
#         data['review_content']['performance_assessment'] = {
#             "assessment_name": performance_assessment.get('assessment_name'),
#             "questions": performance_assessment.get('questions')
#         }

#     # Insert the meeting data into MongoDB
#     meeting_id = talent_review_meeting_collection.insert_one(data).inserted_id
    
#     return jsonify({"message": "Meeting created successfully", "meeting_id": str(meeting_id)}), 201


# if __name__ == '__main__':
#     app.run(debug=True)
















































# import requests
# from datetime import datetime, timedelta
# from pymongo import MongoClient
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # MongoDB client setup (change URI accordingly)
# client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')
# db = client['oras']

# employees_collection = db['HRM_employee_details']
# potential_assessments_collection = db['PGM_potential_assessments']
# performance_assessments_collection = db['PGM_performance_assessments']
# talent_review_meeting_collection = db['PGM_talent_review_meeting']

# # Azure AD credentials
# client_id = '605ca15b-8466-40c1-92f0-681179d37409'
# client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
# tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'

# # Function to get access token from Azure AD
# def get_access_token():
#     url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'scope': 'https://graph.microsoft.com/.default'
#     }
#     response = requests.post(url, headers=headers, data=data)
#     response.raise_for_status()
#     token = response.json().get('access_token', None)
#     if token:
#         return token
#     else:
#         raise Exception("Failed to retrieve access token")

# # Function to get email from the employee details collection by person name
# def get_email_from_name(names_list):
#     emails = []
#     for name in names_list:
#         employee = employees_collection.find_one({"person_name": name})
#         if employee and 'email' in employee:
#             emails.append({'emailAddress': {'address': employee['email'], 'name': name}, 'type': 'required'})
#         else:
#             print(f"Email not found for {name}")
#     return emails

# # Function to get the facilitator's email from the database
# def get_facilitator_email(facilitator_name):
#     facilitator = employees_collection.find_one({"person_name": facilitator_name})
#     if facilitator and 'email' in facilitator:
#         return facilitator['email']
#     return None

# # Function to schedule a Teams meeting
# def create_event_with_teams_link(facilitators, business_leader, review_participants):
#     # Fetch the facilitator's email as the user_email
#     facilitator_email = get_facilitator_email(facilitators[0])  # Assuming first facilitator is the meeting creator

#     if not facilitator_email:
#         print(f"Facilitator {facilitators[0]} not found in HRM_employee_details or no email provided.")
#         return None

#     access_token = get_access_token()

#     if not access_token:
#         print("Failed to retrieve access token")
#         return None

#     # Fetch emails of facilitators, business leader, and review participants
#     attendees = get_email_from_name(facilitators + [business_leader] + review_participants)
    
#     if not attendees:
#         print("No valid attendees found.")
#         return None

#     # Prepare data for creating an event with a Teams meeting link
#     url = f'https://graph.microsoft.com/v1.0/users/{facilitator_email}/events'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json'
#     }
#     data = {
#         'subject': 'Talent Review Meeting',
#         'body': {
#             'contentType': 'HTML',
#             'content': 'This is a talent review meeting with a Teams meeting link.'
#         },
#         'start': {
#             'dateTime': (datetime.now() + timedelta(minutes=30)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'end': {
#             'dateTime': (datetime.now() + timedelta(minutes=60)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'attendees': attendees,
#         'isOnlineMeeting': True,
#         'onlineMeetingProvider': 'teamsForBusiness'
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         event = response.json()
#         if 'webLink' in event:
#             return event['webLink']
#         else:
#             print('Event URL not found in response.')
#             return None

#     except requests.exceptions.HTTPError as http_err:
#         print(f'HTTP error occurred: {http_err}')
#         return None
#     except Exception as err:
#         print(f'Other error occurred: {err}')
#         return None

# # Route to create meeting and schedule a Teams meeting
# @app.route('/create_meeting', methods=['POST'])
# def create_meeting():
#     data = request.json

#     # Fetch potential assessment by name
#     potential_assessment_name = data['review_content'].get('potential_assessment')
#     if potential_assessment_name:
#         potential_assessment = potential_assessments_collection.find_one({"assessment_name": potential_assessment_name})
#         if not potential_assessment:
#             return jsonify({"error": f"Potential assessment '{potential_assessment_name}' not found"}), 400
#         data['review_content']['potential_assessment'] = {
#             "assessment_name": potential_assessment.get('assessment_name'),
#             "questions": potential_assessment.get('questions')
#         }

#     # Fetch performance assessment by name
#     performance_assessment_name = data['review_content'].get('performance_assessment')
#     if performance_assessment_name:
#         performance_assessment = performance_assessments_collection.find_one({"assessment_name": performance_assessment_name})
#         if not performance_assessment:
#             return jsonify({"error": f"Performance assessment '{performance_assessment_name}' not found"}), 400
#         data['review_content']['performance_assessment'] = {
#             "assessment_name": performance_assessment.get('assessment_name'),
#             "questions": performance_assessment.get('questions')
#         }

#     # Fetch meeting attendees
#     facilitators = data['meeting_info'].get('facilitators', [])
#     business_leader = data['meeting_info'].get('business_leader', "")
#     review_participants = data['review_participants']

#     # Schedule the meeting with Teams link
#     event_url = create_event_with_teams_link(facilitators, business_leader, review_participants)
#     if not event_url:
#         return jsonify({"error": "Failed to create Teams meeting"}), 500

#     # Insert the meeting data along with the Teams link into MongoDB
#     data['meeting_info']['teams_meeting_link'] = event_url
#     meeting_id = talent_review_meeting_collection.insert_one(data).inserted_id

#     return jsonify({"message": "Meeting created successfully", "meeting_id": str(meeting_id), "teams_meeting_link": event_url}), 201

# if __name__ == '__main__':
#     app.run(debug=True)


















































































# import requests
# from datetime import datetime, timedelta
# from pymongo import MongoClient
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # MongoDB client setup (change URI accordingly)
# client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')
# db = client['oras']

# employees_collection = db['HRM_employee_details']
# potential_assessments_collection = db['PGM_potential_assessments']
# performance_assessments_collection = db['PGM_performance_assessments']
# talent_review_meeting_collection = db['PGM_talent_review_meeting']
# email_template_collection = db['SCH_email_template']
# email_queue_collection = db['SCH_email_queue']

# # Azure AD credentials
# client_id = '605ca15b-8466-40c1-92f0-681179d37409'
# client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
# tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'

# # Function to get access token from Azure AD
# def get_access_token():
#     url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'scope': 'https://graph.microsoft.com/.default'
#     }
#     response = requests.post(url, headers=headers, data=data)
#     response.raise_for_status()
#     token = response.json().get('access_token', None)
#     if token:
#         return token
#     else:
#         raise Exception("Failed to retrieve access token")

# # Function to get email from the employee details collection by person name
# def get_email_from_name(names_list):
#     emails = []
#     for name in names_list:
#         employee = employees_collection.find_one({"person_name": name})
#         if employee and 'email' in employee:
#             emails.append({'emailAddress': {'address': employee['email'], 'name': name}, 'type': 'required'})
#         else:
#             print(f"Email not found for {name}")
#     return emails

# # Function to get the facilitator's email from the database
# def get_facilitator_email(facilitator_name):
#     facilitator = employees_collection.find_one({"person_name": facilitator_name})
#     if facilitator and 'email' in facilitator:
#         return facilitator['email']
#     return None

# # Function to schedule a Teams meeting
# def create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject):
#     # Fetch the facilitator's email as the user_email
#     facilitator_email = get_facilitator_email(facilitators[0])  # Assuming first facilitator is the meeting creator

#     if not facilitator_email:
#         print(f"Facilitator {facilitators[0]} not found in HRM_employee_details or no email provided.")
#         return None

#     access_token = get_access_token()

#     if not access_token:
#         print("Failed to retrieve access token")
#         return None

#     # Fetch emails of facilitators, business leader, and review participants
#     attendees = get_email_from_name(facilitators + [business_leader] + review_participants)
    
#     if not attendees:
#         print("No valid attendees found.")
#         return None

#     # Prepare data for creating an event with a Teams meeting link
#     url = f'https://graph.microsoft.com/v1.0/users/{facilitator_email}/events'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json'
#     }
#     data = {
#         'subject': meeting_subject,  # Using the input meeting subject dynamically
#         'body': {
#             'contentType': 'HTML',
#             'content': 'This is a talent review meeting with a Teams meeting link.'
#         },
#         'start': {
#             'dateTime': (datetime.now() + timedelta(minutes=30)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'end': {
#             'dateTime': (datetime.now() + timedelta(minutes=60)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'attendees': attendees,
#         'isOnlineMeeting': True,
#         'onlineMeetingProvider': 'teamsForBusiness'
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         event = response.json()
#         if 'webLink' in event:
#             return event['webLink']
#         else:
#             print('Event URL not found in response.')
#             return None

#     except requests.exceptions.HTTPError as http_err:
#         print(f'HTTP error occurred: {http_err}')
#         return None
#     except Exception as err:
#         print(f'Other error occurred: {err}')
#         return None

# # Function to fetch email template from the collection
# def get_email_template(template_name):
#     return email_template_collection.find_one({"template_name": template_name})

# # Function to queue email for sending
# def queue_email(email_data):
#     try:
#         email_data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         email_data["status"] = "pending"
#         result = email_queue_collection.insert_one(email_data)
#         print(f"Email data inserted into the queue successfully with ID: {result.inserted_id}")
#     except Exception as e:
#         print(f"Failed to queue email: {e}")

# # Function to send email to participants and business leader
# def send_emails_to_participants_and_leader(facilitator_name, business_leader, review_participants, meeting_date):
#     # Send email to review participants
#     participant_template = get_email_template("review_participant_notification")
#     if participant_template:
#         for participant in review_participants:
#             email_data = {
#                 "person_name": participant,
#                 "from_email": "no-reply@yourcompany.com",
#                 "template_name": "review_participant_notification",
#                 "data": {
#                     "participant_name": participant,
#                     "facilitator_name": facilitator_name,
#                     "meeting_date": meeting_date
#                 }
#             }
#             queue_email(email_data)
    
#     # Send email to business leader
#     leader_template = get_email_template("business_leader_notification")
#     if leader_template:
#         email_data = {
#             "person_name": business_leader,
#             "from_email": "no-reply@yourcompany.com",
#             "template_name": "business_leader_notification",
#             "data": {
#                 "leader_name": business_leader,
#                 "facilitator_name": facilitator_name,
#                 "meeting_date": meeting_date
#             }
#         }
#         queue_email(email_data)

# # Route to create meeting and schedule a Teams meeting
# @app.route('/create_meeting', methods=['POST'])
# def create_meeting():
#     data = request.json

#     # Fetch potential assessment by name
#     potential_assessment_name = data['review_content'].get('potential_assessment')
#     if potential_assessment_name:
#         potential_assessment = potential_assessments_collection.find_one({"assessment_name": potential_assessment_name})
#         if not potential_assessment:
#             return jsonify({"error": f"Potential assessment '{potential_assessment_name}' not found"}), 400
#         data['review_content']['potential_assessment'] = {
#             "assessment_name": potential_assessment.get('assessment_name'),
#             "questions": potential_assessment.get('questions')
#         }

#     # Fetch performance assessment by name
#     performance_assessment_name = data['review_content'].get('performance_assessment')
#     if performance_assessment_name:
#         performance_assessment = performance_assessments_collection.find_one({"assessment_name": performance_assessment_name})
#         if not performance_assessment:
#             return jsonify({"error": f"Performance assessment '{performance_assessment_name}' not found"}), 400
#         data['review_content']['performance_assessment'] = {
#             "assessment_name": performance_assessment.get('assessment_name'),
#             "questions": performance_assessment.get('questions')
#         }

#     # Fetch meeting attendees
#     facilitators = data['meeting_info'].get('facilitators', [])
#     business_leader = data['meeting_info'].get('business_leader', "")
#     review_participants = data['review_participants']

#     # Get the meeting subject from the input JSON
#     meeting_subject = data['meeting_info'].get('talent_review_meeting', 'Talent Review Meeting')

#     # Schedule the meeting with Teams link
#     event_url = create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject)
#     if not event_url:
#         return jsonify({"error": "Failed to create Teams meeting"}), 500

#     # Insert the meeting data along with the Teams link into MongoDB
#     data['meeting_info']['teams_meeting_link'] = event_url
#     data['meeting_info']['meeting_status'] = "Not started"  # Automatically insert this field
#     meeting_id = talent_review_meeting_collection.insert_one(data).inserted_id

#     # Send notification emails to participants and business leader
#     send_emails_to_participants_and_leader(facilitators[0], business_leader, review_participants, data['meeting_info']['meeting_date'])

#     return jsonify({"message": "Meeting created successfully", "meeting_id": str(meeting_id), "teams_meeting_link": event_url}), 201

# if __name__ == '__main__':
#     app.run(debug=True)












































































# import requests
# from datetime import datetime, timedelta
# from pymongo import MongoClient
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # MongoDB client setup (change URI accordingly)
# client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')
# db = client['oras']

# employees_collection = db['HRM_employee_details']
# potential_assessments_collection = db['PGM_potential_assessments']
# performance_assessments_collection = db['PGM_performance_assessments']
# talent_review_meeting_collection = db['PGM_talent_review_meeting']
# email_template_collection = db['SCH_email_template']
# email_queue_collection = db['SCH_email_queue']

# # Azure AD credentials
# client_id = '605ca15b-8466-40c1-92f0-681179d37409'
# client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
# tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'

# # Function to get access token from Azure AD
# def get_access_token():
#     url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'scope': 'https://graph.microsoft.com/.default'
#     }
#     response = requests.post(url, headers=headers, data=data)
#     response.raise_for_status()
#     token = response.json().get('access_token', None)
#     if token:
#         return token
#     else:
#         raise Exception("Failed to retrieve access token")

# # Function to get email from the employee details collection by person name
# def get_email_from_name(names_list):
#     emails = []
#     for name in names_list:
#         employee = employees_collection.find_one({"person_name": name})
#         if employee and 'email' in employee:
#             emails.append({'emailAddress': {'address': employee['email'], 'name': name}, 'type': 'required'})
#         else:
#             print(f"Email not found for {name}")
#     return emails

# # Function to get the facilitator's email from the database
# def get_facilitator_email(facilitator_name):
#     facilitator = employees_collection.find_one({"person_name": facilitator_name})
#     if facilitator and 'email' in facilitator:
#         return facilitator['email']
#     return None

# # Function to schedule a Teams meeting
# def create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject):
#     # Fetch the facilitator's email as the user_email
#     facilitator_email = get_facilitator_email(facilitators[0])  # Assuming first facilitator is the meeting creator

#     if not facilitator_email:
#         print(f"Facilitator {facilitators[0]} not found in HRM_employee_details or no email provided.")
#         return None

#     access_token = get_access_token()

#     if not access_token:
#         print("Failed to retrieve access token")
#         return None

#     # Fetch emails of facilitators, business leader, and review participants
#     attendees = get_email_from_name(facilitators + [business_leader] + review_participants)
    
#     if not attendees:
#         print("No valid attendees found.")
#         return None

#     # Prepare data for creating an event with a Teams meeting link
#     url = f'https://graph.microsoft.com/v1.0/users/{facilitator_email}/events'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json'
#     }
#     data = {
#         'subject': meeting_subject,  # Using the input meeting subject dynamically
#         'body': {
#             'contentType': 'HTML',
#             'content': 'This is a talent review meeting with a Teams meeting link.'
#         },
#         'start': {
#             'dateTime': (datetime.now() + timedelta(minutes=30)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'end': {
#             'dateTime': (datetime.now() + timedelta(minutes=60)).isoformat(),
#             'timeZone': 'Asia/Kolkata'
#         },
#         'attendees': attendees,
#         'isOnlineMeeting': True,
#         'onlineMeetingProvider': 'teamsForBusiness'
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         event = response.json()
#         if 'webLink' in event:
#             return event['webLink']
#         else:
#             print('Event URL not found in response.')
#             return None

#     except requests.exceptions.HTTPError as http_err:
#         print(f'HTTP error occurred: {http_err}')
#         return None
#     except Exception as err:
#         print(f'Other error occurred: {err}')
#         return None

# # Function to fetch email template from the collection
# def get_email_template(template_name):
#     return email_template_collection.find_one({"template_name": template_name})

# # Function to queue email for sending
# def queue_email(email_data):
#     try:
#         email_data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         email_data["status"] = "pending"
#         result = email_queue_collection.insert_one(email_data)
#         print(f"Email data inserted into the queue successfully with ID: {result.inserted_id}")
#     except Exception as e:
#         print(f"Failed to queue email: {e}")

# # Function to send email notifications to facilitators, participants, and the business leader with the Teams meeting link
# def send_emails_to_participants_and_leader(facilitator_name, business_leader, participants, meeting_date, teams_meeting_link):
#     # Email to Review Participants
#     for participant in participants:
#         template = get_email_template("review_participant_notification")
#         if template:
#             email_data = {
#                 "person_name": participant,
#                 "from_email": "no-reply@yourcompany.com",
#                 "template_name": template["template_name"],
#                 "data": {
#                     "participant_name": participant,
#                     "facilitator_name": facilitator_name,
#                     "meeting_date": meeting_date,
#                     "teams_meeting_link": teams_meeting_link
#                 }
#             }
#             queue_email(email_data)

#     # Email to Business Leader
#     template = get_email_template("business_leader_notification")
#     if template:
#         email_data = {
#             "person_name": business_leader,
#             "from_email": "no-reply@yourcompany.com",
#             "template_name": template["template_name"],
#             "data": {
#                 "leader_name": business_leader,
#                 "facilitator_name": facilitator_name,
#                 "meeting_date": meeting_date,
#                 "teams_meeting_link": teams_meeting_link
#             }
#         }
#         queue_email(email_data)

#     # Email to Facilitator
#     template = get_email_template("facilitator_notification")
#     if template:
#         email_data = {
#             "person_name": facilitator_name,
#             "from_email": "no-reply@yourcompany.com",
#             "template_name": template["template_name"],
#             "data": {
#                 "facilitator_name": facilitator_name,
#                 "meeting_date": meeting_date,
#                 "teams_meeting_link": teams_meeting_link
#             }
#         }
#         queue_email(email_data)

# @app.route('/create_meeting', methods=['POST'])
# def create_meeting():
#     data = request.json

#     # Fetch potential assessment by name
#     potential_assessment_name = data['review_content'].get('potential_assessment')
#     if potential_assessment_name:
#         potential_assessment = potential_assessments_collection.find_one({"assessment_name": potential_assessment_name})
#         if not potential_assessment:
#             return jsonify({"error": f"Potential assessment '{potential_assessment_name}' not found"}), 400
#         data['review_content']['potential_assessment'] = {
#             "assessment_name": potential_assessment.get('assessment_name'),
#             "questions": potential_assessment.get('questions')
#         }

#     # Fetch performance assessment by name
#     performance_assessment_name = data['review_content'].get('performance_assessment')
#     if performance_assessment_name:
#         performance_assessment = performance_assessments_collection.find_one({"assessment_name": performance_assessment_name})
#         if not performance_assessment:
#             return jsonify({"error": f"Performance assessment '{performance_assessment_name}' not found"}), 400
#         data['review_content']['performance_assessment'] = {
#             "assessment_name": performance_assessment.get('assessment_name'),
#             "questions": performance_assessment.get('questions')
#         }

#     # Fetch meeting attendees
#     facilitators = data['meeting_info'].get('facilitators', [])
#     business_leader = data['meeting_info'].get('business_leader', "")
#     review_participants = data['review_participants']

#     # Get the meeting subject from the input JSON
#     meeting_subject = data['meeting_info'].get('talent_review_meeting', 'Talent Review Meeting')

#     # Schedule the meeting with Teams link
#     event_url = create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject)
#     if not event_url:
#         return jsonify({"error": "Failed to create Teams meeting"}), 500

#     # Insert the meeting data along with the Teams link into MongoDB
#     data['meeting_info']['teams_meeting_link'] = event_url
#     data['meeting_info']['meeting_status'] = "Not started"  # Automatically insert this field
#     meeting_id = talent_review_meeting_collection.insert_one(data).inserted_id

#     # Send notification emails to participants, business leader, and facilitator
#     send_emails_to_participants_and_leader(facilitators[0], business_leader, review_participants, data['meeting_info']['meeting_date'], event_url)

#     return jsonify({"message": "Meeting created successfully", "meeting_id": str(meeting_id), "teams_meeting_link": event_url}), 201

# if __name__ == '__main__':
#     app.run(debug=True)




























































from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# MongoDB client setup (change URI accordingly)
client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')
db = client['oras']

employees_collection = db['HRM_employee_details']
email_template_collection = db['SCH_email_template']
email_queue_collection = db['SCH_email_queue']

client_id = '605ca15b-8466-40c1-92f0-681179d37409'
client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'


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

# Function to fetch email of a person by their name
def get_email_of_person(person_name):
    person_record = employees_collection.find_one({"person_name": person_name})
    if person_record and 'email' in person_record:
        return person_record['email']
    else:
        raise Exception(f"Email not found for {person_name}")

# Function to queue email
def queue_email(email_data):
    email_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    email_data['status'] = 'pending'  # Status set to 'pending' for queued emails
    result = email_queue_collection.insert_one(email_data)
    if result.acknowledged:
        print(f"Email queued successfully for {email_data['person_name']}")
        return True
    else:
        print(f"Failed to queue email for {email_data['person_name']}")
        return False

# Function to create an event with a Teams meeting link and retrieve the event URL
def create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject):
    access_token = get_access_token()

    if not access_token:
        print("Failed to retrieve access token")
        return None

    # Get the email of the facilitator who is creating the meeting
    facilitator_name = facilitators[0]  # Assuming the first facilitator is creating the meeting
    user_email = get_email_of_person(facilitator_name)

    # Combine all attendees
    attendees = [
        {'emailAddress': {'address': get_email_of_person(business_leader), 'name': business_leader}, 'type': 'required'}
    ] + [{'emailAddress': {'address': get_email_of_person(participant), 'name': participant}, 'type': 'required'} for participant in review_participants]

    # Add facilitators to attendees
    for facilitator in facilitators:
        attendees.append({'emailAddress': {'address': get_email_of_person(facilitator), 'name': facilitator}, 'type': 'required'})

    # Prepare data for creating an event with a Teams meeting link
    url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'subject': meeting_subject,
        'body': {
            'contentType': 'HTML',
            'content': f'This is a test event with a Teams meeting link for {meeting_subject}.'
        },
        'start': {
            'dateTime': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': (datetime.now() + timedelta(minutes=60)).isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
        'attendees': attendees,
        'isOnlineMeeting': True,
        'onlineMeetingProvider': 'teamsForBusiness', 
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        event = response.json()

        if 'onlineMeeting' in event and 'joinUrl' in event['onlineMeeting']:
            return event['onlineMeeting']['joinUrl']
        else:
            print('Teams meeting URL not found in the response.')
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None

# Function to send notifications
def send_notifications_to_participants(facilitators, business_leader, review_participants, teams_link):
    # Fetch email templates for business leader and review participants
    template_for_participants = email_template_collection.find_one({"template_name": "review_participant_notification"})
    template_for_business_leader = email_template_collection.find_one({"template_name": "business_leader_notification"})
    data = request.json 
    # Send emails to review participants
    for participant in review_participants:
        participant_email = get_email_of_person(participant)
        email_data = {
            "person_name": participant,
            "from_email": "no-reply@yourcompany.com",  # Customize sender's email
            "template_name": "review_participant_notification",  # Template for participants
            "data": {
                "person_name": participant,
                "participant_name":participant,
                "facilitator": facilitators[0],  # The main facilitator
                "meeting_link": teams_link,
                "meeting_date": data['meeting_info']['meeting_date'],
                "teams_meeting_link":teams_link
            }
        }
        queue_email(email_data)

    # Send email to business leader
    business_leader_email = get_email_of_person(business_leader)
    email_data_leader = {
        "person_name": business_leader,
        "from_email": "no-reply@yourcompany.com",  # Customize sender's email
        "template_name": "business_leader_notification",  # Template for business leader
        "data": {
            "person_name": business_leader,
            "facilitator": facilitators[0],  # The main facilitator
            "meeting_link": teams_link,
            "leader_name":business_leader,
            "meeting_date": data['meeting_info']['meeting_date'],
            "teams_meeting_link":teams_link
        }
    }
    queue_email(email_data_leader)

    # Send email to facilitators themselves (optional, if needed)
    for facilitator in facilitators:
        facilitator_email = get_email_of_person(facilitator)
        email_data_facilitator = {
            "person_name": facilitator,
            "from_email": "no-reply@yourcompany.com",  # Customize sender's email
            "template_name": "facilitator_notification",  # Template for facilitators
            "data": {
                "person_name": facilitator,
                "meeting_link": teams_link,
                "facilitator": facilitator,
                "meeting_date": data['meeting_info']['meeting_date'],
                "teams_meeting_link":teams_link
            }
        }
        queue_email(email_data_facilitator)

# Main route to create meeting and send Teams link
@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    data = request.json

    # Extract necessary fields from the input
    facilitators = data['meeting_info']['facilitators']
    business_leader = data['meeting_info']['business_leader']
    review_participants = data['review_participants']
    meeting_subject = data['meeting_info']['talent_review_meeting']

    # Create event and get Teams link
    teams_link = create_event_with_teams_link(facilitators, business_leader, review_participants, meeting_subject)

    if not teams_link:
        return jsonify({"error": "Failed to generate Teams meeting link"}), 500

    # Send notification emails to participants, business leader, and facilitators
    send_notifications_to_participants(facilitators, business_leader, review_participants, teams_link)

    # Save meeting details in MongoDB (if needed)
    return jsonify({"message": "Meeting created successfully", "teams_link": teams_link}), 201

if __name__ == '__main__':
    app.run(debug=True)
