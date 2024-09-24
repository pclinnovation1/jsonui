from datetime import datetime, timedelta
from pymongo import errors, UpdateOne, MongoClient
import config
from eligibility import check_employee_eligibility_for_JRN,check_employee_eligibility_for_task


# MongoDB connection setup
MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = config.DATABASE_NAME

# Set up MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

journey_collection = db[config.JRN_journey]
task_collection = db[config.JRN_task]
employee_collection = db[config.HRM_employee_details]
eligibility_profile_collection = db[config.eligibility_profile_collection]
email_queue = db[config.email_queue]


# Function to queue an email for sending.
# This function accepts a dictionary 'data' containing email information such as 'person_name', 
# 'from_email', 'template_name', 'data', and optionally 'attachments'.
# It constructs an email record with a status of "pending" and inserts it into the 'email_queue' collection.
# If the insertion is successful, it returns a message and the ID of the queued email.
# In case of an exception, it logs the error and returns a failure message.
def queue_email(data):
    try:
        email_data = {
            "person_name": data['person_name'],
            "from_email": data['from_email'],
            "template_name": data['template_name'],
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "data": data['data'],
            "attachments": data.get('attachments', [])
        }
        result = email_queue.insert_one(email_data)
        if result.acknowledged:
            print("Email data inserted into the queue successfully with ID:", result.inserted_id)
            return {"message": "Email data inserted into the queue successfully", "id": str(result.inserted_id)}, True
        else:
            print("Failed to insert email data into the queue")
            return {"message": "Failed to insert email data into the queue"}, False
    except Exception as e:
        print("Exception in queue_email:", str(e))
        return {"message": "Exception occurred while inserting email data into the queue"}, False

# Function to queue an email for sending.
# This function accepts a dictionary 'data' containing email information such as 'person_name', 
# 'from_email', 'template_name', 'data', and optionally 'attachments'.
# It constructs an email record with a status of "pending" and inserts it into the 'email_queue' collection.
# If the insertion is successful, it returns a message and the ID of the queued email.
# In case of an exception, it logs the error and returns a failure message.
def send_overdue_email(journey_data):
    
    task_list_html = "".join(
        f"<li>{task['task_name']} - Due by {task['due_date']} - Overdue by {task['days_overdue']} days</li>"
        for task in journey_data['overdue_tasks']
    )
   
    email_data = {
        "person_name": journey_data['person_name'],
        "from_email": "journey_department",
        "template_name": "tasks_overdue2",  # Ensure this template exists
        "data": {
            "person_name": journey_data['person_name'],
            "journey_name": journey_data['journey_name'],
            "company_name": config.others['company_name'],
            "task_list": task_list_html,
            "current_year": datetime.now().year
        }
    }
    queue_email(email_data)


def get_collection_schema(collection):
    """Retrieve the schema of the collection, excluding the '_id' field."""
    print("Fetching collection schema...")
    sample_document = collection.find_one()
    if not sample_document:
        print("No documents found in collection.")
        return {}
    
    schema = {
        key: type(value).__name__ if value is not None else 'NoneType' 
        for key, value in sample_document.items() 
        if key != '_id'
    }
    
    print(f"Collection schema: {schema}")
    return schema

def validate_data_schema1(schema, data):
    """Validate the data against the schema."""
    print(f"Validating data against schema: {schema}")
    for item in data:
        for key, value in item.items():
            if value is None:
                continue
            if key not in schema or schema[key] != type(value).__name__:
                print(f"Validation failed for key and value: {key} & {value}")
                return False
    print("All items validated successfully.")
    return True

def validate_data_schema2(schema, data):
    """Validate the data against the schema."""
    print(f"Validating data against schema: {schema}")
    for item in data:
        for key in schema.keys():
            if key not in item:
                print(f"Validation failed: missing key '{key}' in item {item}")
                return False
            value = item[key]
            expected_type = schema[key]
            if value is None:
                continue
                # if expected_type != 'NoneType':
                #     print(f"Validation failed for key '{key}': expected type '{expected_type}', got 'NoneType'")
                #     return False
            else:
                actual_type = type(value).__name__
                if actual_type != expected_type:
                    print(f"Validation failed for key '{key}': expected type '{expected_type}', got '{actual_type}'")
                    return False
    print("All items validated successfully.")
    return True

def data_validation_against_schema(collection, data):
    """Perform data validation against the collection schema."""
    schema = get_collection_schema(collection)
    if schema and not validate_data_schema1(schema, data):
        return False
    if schema and not validate_data_schema2(schema, data):
        return False
    return True

def hr_name_fetch(employee):
    return employee.get('hr_name', '')
# -------------------------------------------------------------------

def create_journey(data):
    try:
        # Ensure 'tasks' key exists in the data
        if 'tasks' not in data:
            return {"error": "No tasks provided"}, 400

        # Check if a journey with the same name already exists
        existing_journey = journey_collection.find_one({"journey_name": data.get('journey_name')})
        if existing_journey:
            return {"error": "A journey with this name already exists"}, 400

        # Confirm whether each task exists in the task_collection
        task_names = [task['task_name'] for task in data['tasks']]
        existing_tasks = task_collection.find({"task_name": {"$in": task_names}})

        # Check if all provided tasks are present in the task collection
        existing_task_names = [task['task_name'] for task in existing_tasks]
        missing_tasks = set(task_names) - set(existing_task_names)

        if missing_tasks:
            return {"error": f"Tasks not found: {', '.join(missing_tasks)}"}, 400

        # Step 1: Validate journey-level eligibility profiles
        journey_eligibility_profiles = data.get('eligibility_profiles', [])
        if journey_eligibility_profiles:
            existing_profiles = eligibility_profile_collection.find(
                {"eligibility_profile_definition.name": {"$in": journey_eligibility_profiles}},
                {"eligibility_profile_definition.name": 1, "_id": 0}  # Only return the profile name
            )
            # Extract only the profile names
            existing_profile_names = [profile['eligibility_profile_definition']['name'] for profile in existing_profiles]
            missing_profiles = set(journey_eligibility_profiles) - set(existing_profile_names)

            if missing_profiles:
                return {"error": f"Journey eligibility profiles not found: {', '.join(missing_profiles)}"}, 400

        # Step 2: Validate task-level eligibility profiles
        for task in data['tasks']:
            task_eligibility_profiles = task.get('eligibility_profiles', [])
            if task_eligibility_profiles:
                existing_task_profiles = eligibility_profile_collection.find(
                    {"eligibility_profile_definition.name": {"$in": task_eligibility_profiles}},
                    {"eligibility_profile_definition.name": 1, "_id": 0}  # Only return the profile name
                )
                # Extract only the profile names
                existing_task_profile_names = [profile['eligibility_profile_definition']['name'] for profile in existing_task_profiles]
                missing_task_profiles = set(task_eligibility_profiles) - set(existing_task_profile_names)

                if missing_task_profiles:
                    return {"error": f"Task '{task['task_name']}' eligibility profiles not found: {', '.join(missing_task_profiles)}"}, 400

        # Proceed with journey creation if all tasks and profiles are valid
        data.pop('users', None)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'users' not in data:
            data['users'] = []

        if 'updated_by' not in data:
            data['updated_by'] = 'Admin'
        if 'updated_at' not in data:
            data['updated_at'] = current_time     

        # Validate data against schema
        if not data_validation_against_schema(journey_collection, [data]):
            return {'error': 'Data schema does not match collection schema'}, 400

        # Insert the journey into the collection
        journey_collection.insert_one(data)
        return {"message": "Journey created successfully"}, 201

    except errors.PyMongoError as e:
        return {"error": f"Error inserting data: {e}"}, 500

def create_task(data):
    try:
        # Check if a task with the same name already exists
        existing_task = task_collection.find_one({"task_name": data.get('task_name')})
        if existing_task:
            return {"error": "A task with this name already exists"}, 400

        # Add updated_by and updated_at fields if they don't exist
        data['updated_by'] = data.get('updated_by', 'Admin')
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Validate data against the schema
        if not data_validation_against_schema(task_collection, [data]):
            return {'error': 'Data schema does not match collection schema'}, 400

        # Insert the task into the collection
        task_collection.insert_one(data)
        return {"message": "Task created successfully"}, 201

    except errors.PyMongoError as e:
        return {"error": f"Error inserting data: {e}"}, 500

# Function to add a user to a specific journey.
# This function checks if the user, along with their manager and HR, has already been assigned to the journey. 
# It ensures that the user is not already in progress before assigning the journey.
# 
# - If the user or the user’s manager or HR is already assigned and "In Progress" in the journey, 
#   it returns a message indicating the user is already added.
# - If not, it calls the 'assign_onboarding_journey_with_manager_and_hr' function to assign the journey.
# - After assignment, it updates the journey's "updated_by" and "updated_at" fields.
# 
# Optional: It includes commented-out logic for sending an email notification to the user once assigned.
# Returns a success message if the user is added successfully or an error message in case of exceptions.
def add_user_to_journey(journey_title, user, data):
    try:
        # Retrieve employee details
        employee = employee_collection.find_one({'person_name': user['person_name']})
        if not employee:
            return {'error': 'Employee not found'}, 404
        
        journey1 = journey_collection.find_one({'journey_name': journey_title})
        if not journey1:
            return {'error': 'Journey not found'}, 404
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Check if the user with the same action_name is already added to the journey
        journey = journey_collection.find_one({
            'journey_name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': user['person_name'],
                    'tasks.action_name': user['person_name'],
                    'status': 'In Progress'
                }
            }
        })
        if journey:
            return {'message': f'User is already added to this journey and in progress'}, 200
         # Retrieve employee details, including manager and HR
        employee = employee_collection.find_one({'person_name': user['person_name']})
        manager_name = employee.get("manager_name", None)
        journey2 = journey_collection.find_one({
                                                        'journey_name': journey_title,
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': manager_name,
                                                                'tasks.action_name':user['person_name'],
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
        if journey2:
            return {'message': f'User is already added to this journey and in progress'}, 200
        hr_name = hr_name_fetch(employee)
         
        journey3 = journey_collection.find_one({
                                                        'journey_name': journey_title,
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': hr_name,
                                                                'tasks.action_name': user['person_name'],
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
        if journey3:
            return {'message': f'User is already added to this journey and in progress'}, 200     
        journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey_title, user['person_name'])
        if status_code != 200:
            return journey_response, status_code

        # # Extract the assigned tasks from the response
        # assigned_task_list = journey_response.get('assigned_tasks', {})

        # # Prepare email data
        # employee_email = employee.get('email', '')
        # manager_name = employee.get('manager_name', '')
        # company_name = config.others['company_name']
        # # Prepare the task list for the email
        # task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_task_list)

        journey_collection.update_one(
            {
                'journey_name': journey_title
            },
            {'$set': {"updated_by": data.get('updated_by'),
                       "updated_at":current_time}}
        )
        
        # if employee_email:
        #     # Send email notification to the employee
        #     email_data = {
        #         "to_email": employee_email,
        #         "from_email": config.SMTP_CONFIG['from_email'],
        #         "template_name": config['templates']['user_added_to_journey'],  # Ensure this template exists in your email template collection
        #         "data": {
        #             "person_name": user['person_name'],
        #             "company_name": company_name,
        #             "journey_name": journey_title,
        #             "start_date": datetime.now().strftime('%Y-%m-%d'),
        #             "task_list": task_list_html,
        #             "manager_name": manager_name,
        #             "action_name": user['person_name']
        #         }
        #     }
        #     send_email(email_data)

        return {'message': 'User added successfully and journey assigned'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to assign an onboarding journey to an employee, their manager, and HR.
# This function first checks the eligibility of the employee, manager, and HR for the journey and individual tasks.
# 
# - It retrieves the journey and employee details, including the employee's manager and HR.
# - It checks if the employee, manager, or HR are eligible for the journey and specific tasks.
# - It assigns tasks to the employee, manager, or HR depending on the task's performer role (either 'employee', 'manager', or 'HR').
# - For each eligible entity (employee, manager, or HR), it updates the journey document in the database to include the assigned tasks.
#
# The function returns a success message if the journey is assigned or a failure message if none of the parties are assigned.
# Returns appropriate error messages if the journey or employee is not found, or if there are eligibility issues.
def assign_onboarding_journey_with_manager_and_hr(journey_title, person_name):
    try:
        # Find the journey
        journey = journey_collection.find_one({'journey_name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Retrieve employee details, including manager and HR
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {'error': 'Employee not found'}, 404
      
        if  not check_employee_eligibility_for_JRN(person_name, journey_title):
            return {'error': f'Employee {person_name} is not eligible for journey {journey_title}'}, 403
       
        # Get manager_name and hr_name from the employee record
        manager_name = employee.get("manager_name", None)
        hr_name = hr_name_fetch(employee)
        # Initialize task arrays for employee, manager, and HR
        employee_tasks = []
        manager_tasks = []
        hr_tasks = []
        assigned_tasks=[]
        # Assign tasks based on performer
        for task in journey['tasks']:
            task_info = task_collection.find_one({'task_name': task['task_name']})
            
            if not task_info:
                continue
                # return {'error': f'Task {task['task_name']} not found in task collection'}, 404

            task_due_date = datetime.now() + timedelta(days=task_info['duration'])
            performer = task_info.get('performer').lower()

            # Check eligibility based on the performer
            if performer == "employee":
                print("employee")
                # Check if the employee is eligible for the task
                if not check_employee_eligibility_for_task(person_name, journey_title, task['task_name']):
                    print(f"Employee {person_name} is not eligible for task {task['task_name']}")
                    continue  # Skip the task if the employee is not eligible
                print(f"{person_name} is eligible for {task['task_name']}")

                # Assign task to the employee
                employee_tasks.append({
                    "task_name": task['task_name'],
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "employee",
                    "action_name": person_name  # Use person_name as action_name
                })
                assigned_tasks.append({
                    "task_name": task['task_name'], 
                    "task_due_date": task_due_date.strftime('%Y-%m-%d')
                })

            elif performer == "manager" and manager_name:
                if  not check_employee_eligibility_for_JRN(manager_name, journey_title):
                    print(f'manager {manager_name} is not eligible for journey {journey_title}')
                    continue
                # Check if the manager is eligible for the task
                if not check_employee_eligibility_for_task(manager_name, journey_title, task['task_name']):
                    print(f"Manager {manager_name} is not eligible for task {task['task_name']}")
                    continue  # Skip the task if the manager is not eligible
                print(f"Manager {manager_name} is eligible for {task['task_name']}")
                # Assign task to the manager
                manager_tasks.append({
                    "task_name": task['task_name'],
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "manager",
                    "action_name": person_name  # Use manager_name as action_name
                })

            elif performer == "hr" and hr_name:
                if  not check_employee_eligibility_for_JRN(hr_name, journey_title):
                    print(f'hr {hr_name} is not eligible for journey {journey_title}')
                    continue
                # Check if the HR representative is eligible for the task
                if not check_employee_eligibility_for_task(hr_name, journey_title, task['task_name']):
                    print(f"HR {hr_name} is not eligible for task {task['task_name']}")
                    continue  # Skip the task if HR is not eligible
                print(f"HR {hr_name} is eligible for {task['task_name']}")

                # Assign task to the HR representative
                hr_tasks.append({
                    "task_name": task['task_name'],
                    "status": "Not Started",
                    "task_start_date": datetime.now().strftime('%Y-%m-%d'),
                    "task_due_date": task_due_date.strftime('%Y-%m-%d'),
                    "time_status": "On time",
                    "feedback": "",
                    "performer": "HR",
                    "action_name": person_name  # Use hr_name as action_name
                })
        if employee_tasks: 
            result = journey_collection.update_one(
                {'journey_name': journey_title},
                {'$addToSet': {'users': {
                    'person_name': person_name,
                    'status': 'In Progress',
                    'tasks': employee_tasks  # Employee tasks
                }}}
            )
        if manager_tasks:
            result = journey_collection.update_one(
                {'journey_name': journey_title},
                {'$addToSet': {'users': {
                    'person_name': manager_name,
                    'status': 'In Progress',
                    'tasks': manager_tasks  # Employee tasks
                }}}
            )
        if hr_tasks:    
            result = journey_collection.update_one(
                {'journey_name': journey_title},
                {'$addToSet': {'users': {
                    'person_name': hr_name,
                    'status': 'In Progress',
                    'tasks': hr_tasks  # Employee tasks
                }}}
            )

        if employee_tasks or manager_tasks or hr_tasks:
            return {"message": f"journey assigned to {person_name}, manager, and HR (if applicable)"}, 200
        return {"message": f"no journey assign"}, 501

    except Exception as e:
        return {'error': str(e)}, 500

# Function to add a new task to an existing journey.
# This function checks if the journey and the new task exist in the respective collections.
# It adds the new task, along with its eligibility profiles, to the journey's tasks array.
# - If the task already exists in the journey, it returns a message indicating that the task is already present.
# - If the task is successfully added, it updates the journey's "updated_by" and "updated_at" fields.
# 
# Optionally, the function includes commented-out logic for assigning the new task to individual users in the journey 
# based on their eligibility, which can be implemented if needed.
# Returns a success message if the task is added successfully or an error message in case of exceptions.
def add_task_to_journeyf(journey_title, new_task_name, new_eligibility_profiles,updated_by):
    try:
        # Fetch the journey details
        journey = journey_collection.find_one({'journey_name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404
        
        # Fetch the journey details
        new_task_name1 = task_collection.find_one({'task_name': new_task_name})
        if not new_task_name1:
            return {'error': 'new_task_name not found in task collection'}, 404
        

        # Check if the new task is already in the journey's tasks
        existing_task_names = [task['task_name'] for task in journey.get('tasks', [])]

        # Add the task only if it doesn't exist
        if new_task_name not in existing_task_names:
            # Add the new task with eligibility profiles
            new_task = {
                'task_name': new_task_name,
                'eligibility_profiles': new_eligibility_profiles
            }
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            journey_collection.update_one(
                {'journey_name': journey_title},
                {'$addToSet': {'tasks': new_task}} # Use $addToSet to avoid duplicate entries
            )
            journey_collection.update_one(
            {
                'journey_name': journey_title
            },
            {'$set': {"updated_by": updated_by,
                       "updated_at":current_time}}
        )


        else:
            return {'message': f'Task "{new_task_name}" already exists in the journey'}, 403

        # Optionally, you can assign the new task to individual users or teams here
        # Example for assigning the task to users
        # for user in journey.get('users', []):
        #     if not check_employee_eligibility_for_task(user['person_name'], journey_title, new_task_name):
        #         print(f"User {user['person_name']} is not eligible for task {new_task_name}")
        #         continue  # Skip the user if not eligible
        #     assign_task_to_user(journey_title, user['person_name'], new_task_name)

        return {'message': 'New task added successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to assign onboarding journeys to employees whose start date is today.
# This function:
# 1. Finds unique employees in the 'employee_collection' whose 'effective_start_date' is today.
# 2. Iterates through each employee and assigns an appropriate onboarding journey if they don't already have one.
# 3. For each employee, it also checks the manager and HR to ensure they haven't already been assigned the journey.
# 4. Calls the 'assign_onboarding_journey_with_manager_and_hr' function to assign tasks to the employee, manager, and HR.
# 5. Optionally (commented-out code), sends onboarding emails to employees notifying them of their assigned tasks.
# 
# Returns a success message if journeys are assigned to all eligible employees or an error message if no onboarding journeys are found.
def assign_onboarding_journeys_for_today():
    today = datetime.now().strftime('%Y-%m-%d')
    print(today)
    # Find unique employees with today's start date
    employees = list(employee_collection.aggregate([
        {'$match': {'effective_start_date': today}},
        {'$group': {'_id': '$person_name', 'employee_data': {'$first': '$$ROOT'}}}
    ]))
   
    if not employees:
        return {"message": "No employees found with today's start date"}, 200

    journeys = list(journey_collection.find({}, {'journey_name': 1, 'category': 1, '_id': 0}))

    # Iterate through unique employees
    for employee_entry in employees:
        employee = employee_entry['employee_data']
        person_name = employee["person_name"]
        employment_type = employee["employment_type"].lower()
        grade = employee.get('grade', '')
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')
        start_date = employee.get('effective_start_date', '')

        print(person_name)

        onboarding_journey_found = False

        for journey in journeys:
            category = journey['category']
            # Assign the appropriate journey based on journey category
            if category == config.JRN_boarding_category['onboarding_category']:
                onboarding_journey_found = True
                journey1 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': person_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
                if journey1:
                   continue
                 # Retrieve employee details, including manager and HR
                employee1 = employee_collection.find_one({'person_name': person_name})
                manager_name = employee1.get("manager_name", None)
                journey2 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': manager_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      }) 
                if journey2:
                   continue
                hr_name = hr_name_fetch(employee1)
                journey3 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': hr_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
                
                if journey3:
                   continue
                journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey['journey_name'], person_name)
                if status_code==200:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    journey_collection.update_one(
            {
                'journey_name': journey['journey_name']
            },
            {'$set': {"updated_by": "Admin",
                       "updated_at":current_time}}
        )
            else:
                continue

            # Fetch the list of tasks assigned to the employee
           
            # assigned_tasks = journey_response.get('assigned_tasks', {})

  
            # task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_tasks)
            # action_name = person_name
            # # for task in assigned_tasks:
            # #     action_name = task['action_name']

            # # # Prepare the email data
            # # print(action_name)
            # email_data = {
            #     "to_email": employee_email,
            #     "from_email": config.SMTP_CONFIG['from_email'],
            #     "template_name": config['templates']['onboarding_journey_assigned_today'],
            #     "data": {
            #         "person_name": person_name,
            #         "company_name": config.others['company_name'],
            #         "journey_name": journey['name'],
            #         "start_date": start_date,
            #         "task_list": task_list_html,
            #         "manager_name": manager_name,
            #         "action_name":person_name
            #     }
            # }

            # # Send the onboarding email
            # send_email(email_data)
        if not onboarding_journey_found:
            return {"error": f"No onboarding journey found"}, 404 
    return {"message": "Journeys assigned for all employees starting today"}, 200

# Function to assign offboarding journeys to employees whose end date is today.
# This function:
# 1. Finds unique employees in the 'employee_collection' whose 'effective_end_date' is today.
# 2. Iterates through each employee and assigns an appropriate offboarding journey if they don't already have one.
# 3. For each employee, it also checks the manager and HR to ensure they haven't already been assigned the journey.
# 4. Calls the 'assign_onboarding_journey_with_manager_and_hr' function (which handles both onboarding and offboarding assignment)
#    to assign tasks to the employee, manager, and HR.
# 5. Optionally (commented-out code), sends offboarding emails to employees notifying them of their assigned tasks.
# 
# Returns a success message if journeys are assigned to all eligible employees or an error message if no offboarding journeys are found.
def assign_offboarding_journeys_for_today():
    today = datetime.now().strftime('%Y-%m-%d')
    print(today)
    # Find unique employees with today's start date
    employees = list(employee_collection.aggregate([
        {'$match': {'effective_end_date': today}},
        {'$group': {'_id': '$person_name', 'employee_data': {'$first': '$$ROOT'}}}
    ]))
   
    if not employees:
        return {"message": "No employees found with today's start date"}, 200
    journeys = list(journey_collection.find({}, {'journey_name': 1, 'category': 1, '_id': 0}))

    # Iterate through unique employees
    for employee_entry in employees:
        employee = employee_entry['employee_data']
        person_name = employee["person_name"]
        employment_type = employee["employment_type"].lower()
        grade = employee.get('grade', '')
        employee_email = employee.get('email', '')
        manager_name = employee.get('manager_name', '')
        start_date = employee.get('effective_start_date', '')

        print(person_name)

        onboarding_journey_found = False

        for journey in journeys:
            category = journey['category']

            # Assign the appropriate journey based on worker category
            if category == config.JRN_boarding_category['offboarding_cateogry']:
                onboarding_journey_found = True
                journey1 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': person_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
                if journey1:
                   continue
                 # Retrieve employee details, including manager and HR
                employee1 = employee_collection.find_one({'person_name': person_name})
                manager_name = employee1.get("manager_name", None)
                journey2 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': manager_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      }) 
                if journey2:
                   continue
                hr_name = hr_name_fetch(employee1)
                journey3 = journey_collection.find_one({
                                                        'journey_name': journey['journey_name'],
                                                        'users': {
                                                            '$elemMatch': {
                                                                'person_name': hr_name,
                                                                'tasks.action_name': person_name,
                                                                'status': 'In Progress'
                                                            }
                                                        }
                                                      })
                if journey3:
                   continue
                journey_response, status_code = assign_onboarding_journey_with_manager_and_hr(journey['journey_name'], person_name)
                if status_code==200:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    journey_collection.update_one(
            {
                'journey_name': journey['journey_name']
            },
            {'$set': {"updated_by": "Admin",
                       "updated_at":current_time}}
        )            
            else:
                continue



            # # Fetch the list of tasks assigned to the employee
           
            # assigned_tasks = journey_response.get('assigned_tasks', {})

  
            # task_list_html = "".join(f"<li>{task['task_name']} (Due: {task['task_due_date']})</li>" for task in assigned_tasks)



            # # Prepare the email data
           
            # last_working_day = datetime.now().strftime('%Y-%m-%d')  # Replace with the actual last working day
            # exit_interview_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')  # Example exit interview date

            # email_data = {
            #     "to_email": employee_email,
            #     "from_email": config.SMTP_CONFIG['from_email'],
            #     "template_name": config['templates']['employee_offboarding'],
            #     "data": {
            #         "person_name": person_name,
            #         "company_name": config.others['company_name'],
            #         "last_working_day": last_working_day,
            #         "exit_interview_date": exit_interview_date,
            #         "task_list": task_list_html,
            #         "manager_name": manager_name,
            #         "action_name":person_name
            #     }
            # }

            # # Send the onboarding email
            # send_email(email_data)
        if not onboarding_journey_found:
            return {"error": f"No onboarding journey found"}, 404 
    return {"message": "Journeys Offbaording assigned for all employees ending today"}, 200

# Function to unassign a user from a journey and remove their tasks.
# This function:
# 1. Verifies that the employee exists in the 'employee_collection'.
# 2. Checks if the user is assigned to the journey either by 'person_name' or through task 'action_name'.
# 3. If the user is assigned, it removes the user and their tasks from the journey.
# 4. Updates the journey with 'updated_by' and 'updated_at' fields to record who performed the unassignment.
# 5. Optionally (commented-out code), it also handles sending email notifications to the user and their manager or HR about the unassignment.
#
# Returns a success message if the user is successfully unassigned, or an error message if there is an issue.
def unassign_journey_from_user(journey_title, person_name,updated_by):
    try:
        # Find the journey and check if the user is assigned to it
        # journey = journey_collection.find_one({'name': journey_title, 'users.person_name': person_name})
        
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {"error": f"Employee {person_name} not found in the employee collection"}, 404

        journey = journey_collection.find_one({
            'journey_name': journey_title,
            '$or': [
                {'users.person_name': person_name},
                {'users.tasks.action_name': person_name}
            ]
        })
        if not journey:
            return {'error': f'User {person_name} not found in journey {journey_title}'}, 200

        # Remove the user from the journey
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {'$pull': {'users': {'person_name': person_name}},
            '$set': {
                    'updated_by': updated_by,  # Set the current user who performed the action
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Set the current timestamp
                }}
        )

         # Remove the user from the journey
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {'$pull': {'users': {'tasks.action_name': person_name}},
            '$set': {
                    'updated_by': updated_by,  # Set the current user who performed the action
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Set the current timestamp
                }}
        )
        if result.modified_count == 0:
            return {'error': 'Failed to unassign the user from the journey'}, 500

        # # Get employee email, manager name, and HR name
        # employee = employee_collection.find_one({'person_name': person_name})
        # if employee:
        #     employee_email = employee.get('email', '')
        #     manager_name = employee.get('manager_name', '')
            
        #     hr_name = hr_name_fetch(employee)
        #     print(manager_name+" "+hr_name)
        #     remove_task_and_cleanup_user(journey_title, person_name, manager_name, action_name=person_name)
        #     remove_task_and_cleanup_user(journey_title, person_name, hr_name, action_name=person_name)

        #     if employee_email:
        #         email_data = {
        #             "to_email": employee_email,
        #             "from_email": config.SMTP_CONFIG['from_email'],
        #             "template_name": config['templates']['user_unassigned_from_journey'],
        #             "data": {
        #                 "person_name": person_name,
        #                 "company_name": config.others['company_name'],
        #                 "journey_name": journey_title,
        #                 "manager_name": manager_name,
        #                 "action_name":person_name
        #             }
        #         }
        #         send_email(email_data)

        return {'message': f'User {person_name} successfully unassigned from journey {journey_title} and related tasks removed for manager and HR'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to remove an employee and clean up their associated journeys.
# This function:
# 1. Verifies if the employee exists in the 'employee_collection'.
# 2. Unassigns the employee from all journeys they are part of by calling the 'unassign_journey_from_user' function.
#    It iterates through each journey the employee is part of and removes them from the journey.
# 3. Optionally (commented-out code), it removes the employee from the 'employee_collection' after cleanup.
#
# Returns a success message if the employee is unassigned from all journeys, or an error message if there is an issue.
def remove_employee_and_cleanup_journeys(person_name,updated_by): 
    try:
        # Step 1: Check if the employee exists in the employee collection
        employee = employee_collection.find_one({'person_name': person_name})
        if not employee:
            return {"error": f"Employee {person_name} not found in the employee collection"}, 404

        # Step 2: Unassign the employee from all journeys
        journeys = journey_collection.find(
                {'users.person_name': person_name}
        )
        if journeys:
            for journey in journeys:
                journey_name = journey['journey_name']
                response, status_code = unassign_journey_from_user(journey_name, person_name,updated_by)
                if status_code != 200:
                    return {"error": f"Failed to unassign journey {journey_name} for employee {person_name}: {response.get('error')}"}, 500

        # Step 3: Remove the employee from the employee collection
        # result = employee_collection.delete_one({'person_name': person_name})
        # if result.deleted_count == 0:
        #     return {"error": f"Failed to remove employee {person_name} from the employee collection"}, 500  
        return {"message": f"Employee {person_name} removed successfully and unassigned from all journeys and teams"}, 200
    
    except Exception as e:
        return {"error": str(e)}, 500

# Function to mark a task as completed for a user in a specific journey.
# This function:
# 1. Finds the journey and checks if the user with the specified action_name and task_name is part of it.
# 2. Ensures that the user and task exist in the journey, handling cases where there are multiple user entries.
# 3. Calculates the time status of the task, determining if it was completed on time or late.
# 4. Updates the task status to "Completed" and records the time status (e.g., "Completed on time" or "Completed X day(s) late").
# 5. Optionally (commented-out code), sends an email notification to the user about the task completion.
#
# Returns a success message if the task is marked as completed, or an error message if the task is already completed or if there are issues.
def complete_task(person_name, journey_title, task_name, action_name):
    try:
        # Find the journey and ensure the user with the specific action_name is part of it
        journey = journey_collection.find_one({
            'journey_name': journey_title,
            'users': {
                '$elemMatch': {
                    'person_name': person_name,
                    'status':'In Progress',
                    'tasks.task_name': task_name,
                    'tasks.action_name': action_name
                }
            }
        })
        if not journey:
            return {'error': 'Please provide correct data'}, 404
        
         # Step 2: Find the user entries that match the person_name and ensure multiple entries are handled
        user_entries = [
            user for user in journey.get('users', [])
            if user.get('person_name') == person_name and
            any(task.get('task_name') == task_name and task.get('action_name') == action_name for task in user.get('tasks', []))
        ]

        if not user_entries:
            return {'error': 'User not found in the journey'}, 404

        # Step 3: Select the latest entry (assumes last entry is the latest, could be by timestamp if available)
        user = user_entries[-1]  # Get the last entry for this user
        print(user)
        # Step 4: Find the correct task within that user's entry
        task = next(
            (task for task in user.get('tasks', [])
             if task.get('task_name') == task_name and task.get('action_name') == action_name), 
            None
        )

        if not task:
            return {'error': 'Task not found'}, 404

        # # Ensure the user exists in the journey with the correct action_name
        # user = next(
        #     (user for user in journey.get('users', []) 
        #      if user.get('person_name') == person_name and 
        #         any(task.get('action_name') == action_name for task in user.get('tasks', []))
        #     ), 
        #     None
        # )
        
        # if not user:
        #     return {'error': 'User not found in the journey'}, 404

        # # Ensure the task exists for the user with the correct action_name
        # task = next(
        #     (task for task in user.get('tasks', []) 
        #      if task.get('task_name') == task_name and task['action_name'] == action_name), 
        #     None
        # )
        
        # if not task:
        #     return {'error': 'Task not found'}, 404

        # Calculate time status
        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d')
        current_date = datetime.now()
        time_status = "Completed on time" if current_date <= due_date else f"Completed {current_date - due_date} day(s) late"

        # Update the task status using the user's person_name and action_name
        result = journey_collection.update_one(
            {
                'journey_name': journey_title,
                'users.person_name': person_name,
                'users.status':'In Progress',
                'users.tasks.task_name': task_name,
                'users.tasks.action_name': action_name
            },
            {
                '$set': {
                    'users.$[user].tasks.$[task].status': 'Completed',
                    'users.$[user].tasks.$[task].time_status': time_status
                }
            },
            array_filters=[
                {'user.person_name': person_name,'user.status': 'In Progress'},
                {'task.task_name': task_name,'task.action_name': action_name}
            ]
        )
        print(result)
        if result.modified_count == 0:
            return {'error': 'Task is already mark completed'}, 500
        
        # # Retrieve the employee's email and manager name for notification
        # employee = employee_collection.find_one({'person_name': person_name})
        # if not employee:
        #     return {'error': 'Employee not found'}, 404
        
        # employee_email = employee.get('email', '')
        # manager_name1 = employee.get('manager_name', '')

        # # Send email notification
        # email = {
        #     "to_email": employee_email,
        #     "from_email": config.SMTP_CONFIG['from_email'],
        #     "template_name": config['templates']['task_complete'],
        #     "data": {
        #         "journey_title":journey_title,
        #         "person_name": person_name,
        #         "task_name": task_name,
        #         "completion_date": current_date.strftime('%B %d, %Y'),  # Format the date
        #         "task_status": time_status,
        #         "manager_name": manager_name1,
        #         "action_name":action_name,
        #         "company_name":config.others['company_name']
        #     }
        # }
        # # Uncomment to send the email
        # send_email(email)

        return {'message': 'Task marked as completed'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to update the status of users in all journeys based on their task completion status.
# This function:
# 1. Fetches all journeys from the 'journey_collection'.
# 2. Iterates through each journey and checks the status of each user's tasks.
# 3. If all tasks for a user are marked as 'Completed', the user's status is updated to 'Completed'.
# 4. If any tasks are still in progress, the user's status remains 'In Progress'.
# 5. Updates the journey in the database with the modified user status.
#
# Returns a success message if the statuses are updated successfully, or an error message if there is an issue.
def update_status_for_completed_tasks():
    try:
        # Fetch all journeys
        journeys = list(journey_collection.find({}))

        for journey in journeys:
            # Check for users
            if 'users' in journey and isinstance(journey['users'], list):
                for user in journey['users']:
                    tasks = user.get('tasks', [])
                    if tasks and all(task['status'] == 'Completed' for task in tasks):
                        user['status'] = 'Completed'
                    else:
                        user['status'] = 'In Progress'
                # Update the journey with the new user status
                journey_collection.update_one(
                    {'_id': journey['_id']},
                    {'$set': {'users': journey['users']}}
                )

        return {'message': 'Statuses updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to update a task's details in the task collection.
# This function:
# 1. Updates the specified task in the 'task_collection' based on the 'task_name' and the provided 'update_data'.
# 2. Additionally, it updates the 'updated_at' field with the current timestamp after the task is updated.
# 3. Optionally (commented-out code), it can notify users assigned to the task via email.
#    The function retrieves all journeys where the task is assigned and sends email notifications to the users.
#
# Returns a success message if the task is updated, or an error message if the task is not found or if there is an issue.
def update_task(task_name, update_data):
    try:
        # Update the task in the JRN_task collection
        result = task_collection.update_one(
            {'task_name': task_name},
            {'$set': update_data}
        )
        
        task_collection.update_one(
            {'task_name': task_name},
            {'$set': {
                       "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
        )

        if result.matched_count == 0:
            return {'error': 'Task not found'}, 404

        # # Get the task details
        # task = task_collection.find_one({'task_name': task_name})
        # if task is None:
        #     return {'error': f'Task {task_name} not found after update'}, 404
        
        # updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # updated_by = update_data.get('updated_by', 'System')

        # # Find all journeys where this task is assigned
        # journeys = journey_collection.find({'users.tasks.task_name': task_name})

        # for journey in journeys:
        #     # Notify individual users
        #     for user in journey['users']:
        #         user_tasks = [t for t in user.get('tasks', []) if t['task_name'] == task_name]
                
        #         if user_tasks:
        #             person_name = user.get('person_name', None)
        #             if not person_name:
        #                 continue  # Skip if person_name is not available

        #             employee = employee_collection.find_one({'person_name': person_name})
        #             if employee is None:
        #                 continue  # Skip if employee record is not found

        #             employee_email = employee.get('email', None)
        #             if not employee_email:
        #                 continue  # Skip if employee email is not available

        #             # Prepare the email for each user assigned to the task
        #             action_name = person_name
        #             for task in user_tasks:
        #                 action_name=task['action_name']

        #             email = {
        #                 "to_email": employee_email,
        #                 "from_email": config.SMTP_CONFIG['from_email'],
        #                 "template_name": config['templates']['task_updated'],
        #                 "data": {
        #                     "journey_name":journey['name'],
        #                     "task_name": task_name,
        #                     "person_name": person_name,
        #                     "updated_by": updated_by,
        #                     "update_date": update_date,
        #                     "company_name": config.others['company_name'],
        #                     "action_name":action_name
        #                 }
        #             }
        #             send_email(email)

  
        return {'message': 'Task updated successfully and notifications sent'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to update a journey's details such as category, description, and update information.
# This function:
# 1. Updates the specified journey in the 'journey_collection' based on the provided 'journey_title', 'category', 'description', and 'updated_by'.
# 2. Additionally, it updates the 'updated_at' field with the current timestamp and records who performed the update via 'updated_by'.
# 3. Optionally (commented-out code), the function can notify users assigned to the journey via email about the update.
#    It retrieves the users in the journey and sends notification emails to them.
#
# Returns a success message if the journey is updated, or an error message if the journey is not found or if there is an issue.
def update_journey(journey_title, category, description, updated_by):
    try:
        updated_data={'updated_by':updated_by,
            'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        if category:
          updated_data['category']=category 
        if description:
          updated_data['description']=description   
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {'$set': updated_data}
        )

        if result.matched_count == 0:
            return {'error': 'Journey not found'}, 404

        # # Fetch the journey after update
        # journey = journey_collection.find_one({'name': journey_title})
        # users = journey.get('users', [])

        # # Notify each user in the journey
        # for user in users:
        #     employee = employee_collection.find_one({'person_name': user['person_name']})
        #     tasks = user.get('tasks', [])
        #     action_name = user['person_name']
        #     for task in tasks:
        #             action_name = task.get('action_name', user['person_name'])
        #     if employee:
        #         employee_email = employee.get('email', '')
        #         # print(employee_email)
        #         if employee_email:
        #             email_data = {
        #                 "to_email": employee_email,
        #                 "from_email": config.SMTP_CONFIG['from_email'],
        #                 "template_name": config['templates']['journey_updated'],  # Ensure this template exists in your email template collection
        #                 "data": {
        #                     "person_name": user['person_name'],
        #                     "journey_name": journey_title,
        #                     "updated_at": update_data['updated_at'],
        #                     "company_name": config.others['company_name'],
        #                     "action_name":action_name
        #                 }
        #             }
        #             send_email(email_data)

        return {'message': 'Journey updated successfully and notifications sent'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to delete a journey from the journey collection.
# This function:
# 1. Deletes the journey specified by the 'journey_title' from the 'journey_collection'.
# 2. If the journey is not found, it returns an error message.
# 3. If the journey is successfully deleted, it returns a success message.
#
# Returns a success message if the journey is deleted, or an error message if the journey is not found or if there is an issue.
def delete_journey(journey_title):
    try:
        result = journey_collection.delete_one({'journey_name': journey_title})

        if result.deleted_count == 0:
            return {'error': 'Journey not found'}, 404
       
        
        return {'message': 'Journey deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to delete a task from the task collection and remove it from all journeys.
# This function:
# 1. Checks if the task exists in the 'task_collection'. If not, it returns a message indicating the task was not found.
# 2. If the task exists, it deletes the task from the 'task_collection'.
# 3. Removes the task from the 'tasks' array in all journeys that include it in the 'journey_collection'.
# 4. Updates the 'updated_by' and 'updated_at' fields in the journeys to record who performed the deletion and the timestamp.
#
# Returns a success message if the task is deleted and removed from journeys, or an error message if an issue occurs.
def delete_task(task_name,updated_by):
    try:
        result1 = task_collection.find_one({'task_name': task_name})
        if not result1:
           return {'message': 'Task not found'}, 200
        task_collection.delete_one({'task_name': task_name})


        # Step 2: Remove the task from the tasks array in all journeys in journey_collection
        journey_collection.update_many(
            {'tasks.task_name': task_name},
            {'$pull': {'tasks': {'task_name': task_name}},
             '$set': {
                    'updated_by': updated_by,  # Set the current user who performed the action
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Set the current timestamp
                }}
        )
          
        return {'message': 'Task deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to submit feedback for a specific task in a journey.
# This function:
# 1. Finds the journey document and retrieves the 'users' array containing user and task data.
# 2. Locates all entries for the user specified by 'person_name', checking if the user has performed the given task.
# 3. Selects the most recent (last) user entry if multiple exist.
# 4. Finds the specific task in the selected user entry and verifies if the task exists.
# 5. Checks if the feedback has already been submitted for the task. If so, it returns a message indicating feedback was already submitted.
# 6. Updates the feedback for the task in the last user entry.
#
# Returns a success message if feedback is submitted, or an error message if any issues arise (e.g., user or task not found).
def submit_feedback(person_name, journey_title, task_name, action_name, feedback):
    try:
        # Step 1: Find the journey document and retrieve users array
        journey = journey_collection.find_one({
            'journey_name': journey_title,
            'users.person_name': person_name
        }, {'users': 1})  # Fetch only the users array to optimize query

        if not journey:
            return {'error': 'Please provide correct data'}, 404

        # Step 2: Get the users array and find the indices of all matching user entries
        users = journey.get('users', [])
        user_indices = [
            index for index, user in enumerate(users)
            if user.get('person_name') == person_name and
            any(task.get('task_name') == task_name and task.get('action_name') == action_name for task in user.get('tasks', []))
        ]

        if not user_indices:
            return {'error': 'User not found in the journey'}, 404

        # Step 3: Select the index of the last user entry
        last_user_index = user_indices[-1]  # Get the index of the last matching user entry

        # Step 4: Find the correct task within the last user's entry
        tasks = users[last_user_index].get('tasks', [])
        task_index = next(
            (index for index, task in enumerate(tasks)
             if task.get('task_name') == task_name and task.get('action_name') == action_name),
            None
        )

        if task_index is None:
            return {'error': 'Task not found'}, 404

        # Step 5: Check if the feedback is already submitted
        if tasks[task_index].get('feedback') == feedback:
            return {'message': 'Feedback has already been submitted'}, 200

        # Step 6: Update the feedback for the specific task in the last user's entry
        result = journey_collection.update_one(
            {
                'journey_name': journey_title
            },
            {
                '$set': {
                    f'users.{last_user_index}.tasks.{task_index}.feedback': feedback  # Update specific task in the last user entry
                }
            }
        )

        if result.modified_count == 0:
            return {'error': 'Failed to submit feedback'}, 500

        return {'message': 'Feedback submitted successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to remove a specific task from a journey.
# This function:
# 1. Fetches the journey details from the 'journey_collection' based on the provided 'journey_title'.
# 2. Uses the '$pull' operator to remove the task with the matching 'task_name' from the 'tasks' array in the journey.
# 3. Updates the 'updated_at' field to record the current time and the 'updated_by' field to record who performed the removal.
# 4. If the task is not found or cannot be removed, it returns an error message.
#
# Returns a success message if the task is removed from the journey, or an error message if the journey or task is not found or if any issue occurs.
def remove_task_from_journey(journey_title, task_name_to_remove, updated_by):
    try:
        # Step 1: Fetch the journey details
        journey = journey_collection.find_one({'journey_name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Step 2: Use $pull to remove the task by task_name
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {'$pull': {'tasks': {'task_name': task_name_to_remove}},
                '$set': {
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Update the updated_at field with the current time
                    'updated_by': updated_by  # Update the updated_by field with the provided user
                }
             
             }
        )

        if result.modified_count == 0:
            return {'error': f"Task '{task_name_to_remove}' not found or could not be removed."}, 404

        return {'message': f"Task '{task_name_to_remove}' removed from journey successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to update the time status of tasks in all journeys based on the current date.
# This function:
# 1. Fetches all journeys from the 'journey_collection'.
# 2. Iterates through each user and their tasks in the journey, checking the 'task_due_date'.
# 3. If the task is completed, it skips the update.
# 4. If the current date is before or equal to the task's due date, it sets the 'time_status' to "On time".
#    If the task is overdue, it calculates how many days overdue and updates the 'time_status' accordingly.
# 5. Performs bulk updates for tasks where the 'time_status' has changed.
#
# Returns a success message if time statuses are updated, or an error message if any issues occur.
def update_time_status():
    try:
        current_date = datetime.now().date()
        updates = []

        journeys = list(journey_collection.find({}))
        for journey in journeys:
            if 'users' in journey and isinstance(journey['users'], list):
                for user_index, user in enumerate(journey['users']):
                    if 'tasks' in user and isinstance(user['tasks'], list):
                        for task_index, task in enumerate(user['tasks']):
                            if isinstance(task, dict) and 'status' in task and task['status'] == 'Completed':
                                continue
                            if isinstance(task, dict) and 'task_due_date' in task and 'task_name' in task:
                                due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                                if current_date <= due_date:
                                    time_status = 'On time'
                                else:
                                    time_status = f'Overdue by {(current_date - due_date).days} days'
                                if 'time_status' in task and task['time_status'] != time_status:
                                    updates.append(UpdateOne(
                                        {'_id': journey['_id'], f'users.{user_index}.tasks.{task_index}.task_name': task['task_name']},
                                        {'$set': {f'users.{user_index}.tasks.{task_index}.time_status': time_status}}
                                    ))

        if updates:
            journey_collection.bulk_write(updates)
        return {'message': 'Time statuses updated successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Function to send notifications for overdue tasks in all journeys.
# This function:
# 1. Fetches all journeys from the 'journey_collection'.
# 2. Iterates through each user in the journey and checks their tasks.
# 3. For tasks that are not completed and are past their due date, it calculates how many days they are overdue.
# 4. If there are overdue tasks for a user, it gathers the task details and sends an email notification to the user.
# 5. Emails are only sent to users who have overdue tasks.
#
# Returns a success message if notifications are sent, or an error message if an issue occurs.
def send_overdue_task_notifications():
    try:
        # Get the current date
        current_date = datetime.now().date()

        # Fetch all journeys from the collection
        journeys = journey_collection.find()

        for journey in journeys:
            # Iterate through all users in the journey
            for user in journey.get('users', []):
                overdue_tasks = []
                for task in user.get('tasks', []):
                    if task['status'] != 'Completed':
                        due_date = datetime.strptime(task['task_due_date'], '%Y-%m-%d').date()
                        if current_date > due_date:
                            days_overdue = (current_date - due_date).days
                            overdue_tasks.append({
                                'task_name': task['task_name'],
                                'due_date': due_date.strftime('%Y-%m-%d'),
                                'days_overdue': days_overdue
                            })

                # Send email if there are overdue tasks
                employee = employee_collection.find_one({'person_name': user['person_name']})
                if not employee:
                    continue
                if overdue_tasks:
                    prep_data={
                                "person_name": user['person_name'],
                                "overdue_tasks": overdue_tasks,
                                "journey_name": journey.get('journey_name')
                        }
                    send_overdue_email(prep_data)

        return {"message": "Overdue task notifications sent"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# Function to add an eligibility profile to a journey.
# This function:
# 1. Fetches the journey details from the 'journey_collection' based on the provided 'journey_title'.
# 2. Checks if the eligibility profile exists in the 'eligibility_profile_collection'.
# 3. Verifies whether the profile is already added to the journey's 'eligibility_profiles' array to avoid duplication.
# 4. If the profile is not already present, it uses '$addToSet' to add the profile and updates the 'updated_at' and 'updated_by' fields.
# 5. Returns an error if the profile cannot be added, or if the profile is already present.
#
# Returns a success message if the eligibility profile is added to the journey, or an error message if the profile or journey is not found, or if there is an issue.
def add_eligibility_profile(journey_title, eligibility_profile_to_add, updated_by):
    try:
        # Step 1: Fetch the journey details
        journey = journey_collection.find_one({'journey_name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        profile = eligibility_profile_collection.find_one({'eligibility_profile_definition.name': eligibility_profile_to_add})
        
        if not profile:
            return {'error': 'profile  not found'}, 404 # Profile does not exist

        # Step 2: Check if the profile already exists in the array
        if eligibility_profile_to_add in journey.get('eligibility_profiles', []):
            return {'error': f"Eligibility profile '{eligibility_profile_to_add}' already exists."}, 400

        # Step 3: Use $addToSet to add the profile and update the fields
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {
                '$addToSet': {'eligibility_profiles': eligibility_profile_to_add},  # Add profile only if it's not already there
                '$set': {
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Update the updated_at field
                    'updated_by': updated_by  # Set the updated_by field
                }
            }
        )

        if result.modified_count == 0:
            return {'error': 'Failed to add eligibility profile.'}, 500

        return {'message': f"Eligibility profile '{eligibility_profile_to_add}' added successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to remove an eligibility profile from a journey.
# This function:
# 1. Fetches the journey details from the 'journey_collection' based on the provided 'journey_title'.
# 2. Checks if the eligibility profile exists in the journey's 'eligibility_profiles' array.
# 3. If the profile is found, it uses '$pull' to remove the profile and updates the 'updated_at' and 'updated_by' fields.
# 4. Returns an error if the profile does not exist or cannot be removed.
#
# Returns a success message if the eligibility profile is removed from the journey, or an error message if the profile or journey is not found, or if there is an issue.
def remove_eligibility_profile(journey_title, eligibility_profile_to_remove, updated_by):
    try:
        # Step 1: Fetch the journey details
        journey = journey_collection.find_one({'journey_name': journey_title})
        if not journey:
            return {'error': 'Journey not found'}, 404

        # Step 2: Check if the profile exists in the array
        if eligibility_profile_to_remove not in journey.get('eligibility_profiles', []):
            return {'error': f"Eligibility profile '{eligibility_profile_to_remove}' does not exist."}, 404

        # Step 3: Use $pull to remove the profile and update the fields
        result = journey_collection.update_one(
            {'journey_name': journey_title},
            {
                '$pull': {'eligibility_profiles': eligibility_profile_to_remove},  # Remove the profile from the array
                '$set': {
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Update the updated_at field
                    'updated_by': updated_by  # Set the updated_by field
                }
            }
        )

        if result.modified_count == 0:
            return {'error': 'Failed to remove eligibility profile.'}, 500

        return {'message': f"Eligibility profile '{eligibility_profile_to_remove}' removed successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to add an eligibility profile to a specific task within a journey.
# This function:
# 1. Fetches the journey and verifies that the task exists in the 'tasks' array of the journey.
# 2. Checks if the eligibility profile exists in the 'eligibility_profile_collection'.
# 3. Adds the eligibility profile to the specific task's 'eligibility_profiles' array using '$addToSet' to avoid duplicates.
# 4. Updates the 'updated_at' and 'updated_by' fields to track when and by whom the profile was added.
# 5. Returns an error if the journey, task, or profile is not found, or if the update fails.
#
# Returns a success message if the eligibility profile is added to the task, or an error message if there is an issue.
def add_task_eligibility_profile(journey_title, task_name, eligibility_profile_to_add, updated_by):
    try:
        # Step 1: Find the journey and ensure the task exists
        journey = journey_collection.find_one({
            'journey_name': journey_title,
            'tasks.task_name': task_name
        })

        if not journey:
            return {'error': 'Journey or task not found'}, 404
        
        profile = eligibility_profile_collection.find_one({'eligibility_profile_definition.name': eligibility_profile_to_add})
        
        if not profile:
            return {'error': 'profile  not found'}, 404 # Profile does not exist

        # Step 2: Add the eligibility profile to the task using $addToSet and the $ positional operator
        result = journey_collection.update_one(
            {
                'journey_name': journey_title,
                'tasks.task_name': task_name  # Target the task inside the journey
            },
            {
                '$addToSet': {
                    'tasks.$.eligibility_profiles': eligibility_profile_to_add  # Add to the specific task's eligibility_profiles array
                },
                '$set': {
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Update the updated_at field
                    'updated_by': updated_by  # Set the updated_by field
                }
            }
        )

        if result.modified_count == 0:
            return {'error': 'Failed to add eligibility profile to the task.'}, 500

        return {'message': f"Eligibility profile '{eligibility_profile_to_add}' added to task '{task_name}' successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Function to remove an eligibility profile from a specific task within a journey.
# This function:
# 1. Fetches the journey and ensures the task exists within the 'tasks' array of the journey.
# 2. Uses '$pull' to remove the eligibility profile from the specific task's 'eligibility_profiles' array.
# 3. Updates the 'updated_at' and 'updated_by' fields to track when and by whom the profile was removed.
# 4. Returns an error if the journey, task, or profile is not found, or if the update fails.
#
# Returns a success message if the eligibility profile is removed from the task, or an error message if there is an issue.
def remove_task_eligibility_profile(journey_title, task_name, eligibility_profile_to_remove, updated_by):
    try:
        # Step 1: Find the journey and ensure the task exists
        journey = journey_collection.find_one({
            'journey_name': journey_title,
            'tasks.task_name': task_name
        })

        if not journey:
            return {'error': 'Journey or task not found'}, 404

        # Step 2: Remove the eligibility profile from the task using $pull and the $ positional operator
        result = journey_collection.update_one(
            {
                'journey_name': journey_title,
                'tasks.task_name': task_name,
                'tasks.eligibility_profiles': eligibility_profile_to_remove  
            },
            {
                '$pull': {
                    'tasks.$.eligibility_profiles': eligibility_profile_to_remove  # Remove from the specific task's eligibility_profiles array
                },
                '$set': {
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Update the updated_at field
                    'updated_by': updated_by  # Set the updated_by field
                }
            }
        )

        if result.modified_count == 0:
            return {'error': 'Failed to remove eligibility profile from the task or profile not found.'}, 500

        return {'message': f"Eligibility profile '{eligibility_profile_to_remove}' removed from task '{task_name}' successfully."}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# -----------------------------------------------------------------------------------------------------
