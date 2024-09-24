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

def delete_journey(journey_title):
    try:
        result = journey_collection.delete_one({'journey_name': journey_title})

        if result.deleted_count == 0:
            return {'error': 'Journey not found'}, 404
       
        
        return {'message': 'Journey deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

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
