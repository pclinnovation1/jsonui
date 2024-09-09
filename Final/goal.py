from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from jsonschema import validate, ValidationError
# from algorithms.general_algo import get_database

# Initialize Blueprint for goal
goal_bp = Blueprint('add_goal_bp', __name__)

# MongoDB connection setup 
MONGODB_URI ="mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

# Set up MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# MongoDB collections
my_goals_collection = db['PGM_my_goals']
goals_collection = db["PGM_goal"]
employee_details_collection = db["HRM_employee_details"]
employee_personal_details_collection = db["HRM_personal_details"]
employee_salary_details_collection = db["HRM_salary_details"]
derived_employee_collection = db['HRM_employee_derived_details']
eligibility_profiles_collection = db["PGM_eligibility_profiles"]
goal_plan_collection = db["PGM_goal_plan"]
my_goals_plan_collection = db["PGM_my_goal_plan_goals"]
goal_offering_collection= db["PGM_goal_offering"]
mass_assign=db["PGM_mass_assign_process"]


def queue_email(data):
    try:
        email_data = {
            "to_email": data['to_email'],
            "from_email": data['from_email'],
            "template_name": data['template_name'],
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "data": data['data'],
            "attachments": data.get('attachments', [])
        }
        result = db['SCH_email_queue'].insert_one(email_data)
        if result.acknowledged:
            print("Email data inserted into the queue successfully with ID:", result.inserted_id)
            return {"message": "Email data inserted into the queue successfully", "id": str(result.inserted_id)}, True
        else:
            print("Failed to insert email data into the queue")
            return {"message": "Failed to insert email data into the queue"}, False
    except Exception as e:
        print("Exception in queue_email:", str(e))
        return {"message": "Exception occurred while inserting email data into the queue"}, False

def send_email_on_goal_assignment(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_assigned",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "goal_type": goal_data["goal_type"]
        }
    }
    queue_email(email_data)

def send_email_on_goal_offering(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_offering_request",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "status": goal_data["status"]
        }
    }
    queue_email(email_data)
 
def send_email_on_goal_progress_updated(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_progress_updated",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "status": goal_data["status"]
        }
    }
    queue_email(email_data)

def send_email_on_goal_task_progress_update(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_task_updated",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "status": goal_data["status"]
        }
    }
    queue_email(email_data)

def send_email_on_goal_task_completion_update(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_task_completion_updated",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "status": goal_data["status"]
        }
    }
    queue_email(email_data)

def send_email_on_feedback_of_goal(goal_data):
    email_data = {
        "person_name": goal_data["person_name"],
        "from_email": "PGM_department",
        "template_name": "goal_feedback",
        "data": {
            "person_name": goal_data["person_name"],
            "goal_name": goal_data["goal_name"],
            "goal_plan_assigned": goal_data["goal_plan_assigned"],
            "status": goal_data["status"]
        }
    }
    queue_email(email_data)

# Helper function to convert keys to lowercase and replace spaces with underscores
# This function is recursive, works for both dictionaries and lists
def lowercase_keys(data):
    if isinstance(data, dict):
        # For dictionary, convert keys and apply recursively
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        # For list, apply recursively on all elements
        return [lowercase_keys(item) for item in data]
    else:
        return data # Base case: return the data if neither dict nor list

# Helper function to check if a field exists in the MongoDB collection
# This checks for the existence of a particular field in any document in the collection
def field_exists(collection, field_name):
    return collection.find_one({field_name: {"$exists": True}}) is not None

# Function to construct a MongoDB query based on provided criteria
# This creates a query dict for MongoDB based on criteria passed
def construct_query(criteria, collection):
    query = {}
    for key, value in criteria.items():
        if isinstance(value, str):
            if value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()  # Ensure field names are also lowercase
                
                # Convert both field name and value to lowercase for case-insensitive matching
                if field_exists(collection, field_name):
                    query[field_name] = {"$regex": f"^{value}$", "$options": "i"}  # Case-insensitive regex match
        elif isinstance(value, (int, float, bool)):
            # Direct match for non-string values like int, float, bool
            field_name = key.replace(' ', '_').lower()
            if field_exists(collection, field_name):
                query[field_name] = value
                
    return query

# Function to retrieve matching employees based on profile
# This queries the MongoDB collection to get employees matching the profile
def get_matching_employees(profile):
    matched_employees = set()
    criteria = profile["eligibility_criteria"]

    # Combine all criteria from the different sections
    all_criteria = {
        **criteria.get("personal", {}),
        **criteria.get("employment", {}),
        **criteria.get("derived_factors", {}),
        **criteria.get("other", {}),
        **criteria.get("labor_relations", {}),
    }

 
    query_for_employee_details = construct_query(all_criteria, employee_details_collection)
    query_for_employee_personal_details = construct_query(all_criteria, employee_personal_details_collection)
    query_for_employee_salary_details = construct_query(all_criteria, employee_salary_details_collection)
    query_for_derived_employee_details = construct_query(all_criteria, derived_employee_collection)
 


    employees = list(employee_details_collection.find(query_for_employee_details))
    employee_personal_details = list(employee_personal_details_collection.find(query_for_employee_personal_details))
    employee_salary_details = list(employee_salary_details_collection.find(query_for_employee_salary_details))
    derived_employees = list(derived_employee_collection.find(query_for_derived_employee_details))
    

    employee_names_from_employee_details = {employee.get('person_name') for employee in employees}
    employee_names_from_employee_personal_details = {employee.get('person_name') for employee in employee_personal_details}
    employee_names_from_employee_salary_details = {employee.get('person_name') for employee in employee_salary_details}
    employee_names_from_derived = {employee.get('person_name') for employee in derived_employees}


    common_employee_names = employee_names_from_employee_details.intersection(employee_names_from_employee_personal_details)
    common_employee_names1 = employee_names_from_employee_salary_details.intersection(common_employee_names)
    common_employee_names2 = common_employee_names1.intersection(employee_names_from_derived)

    matched_employees.update(common_employee_names2)

    return list(matched_employees)

#goal schema to check whether given input is in correct format or not 
goal_schema = {
    "type": "object",
    "properties": {
        "basic_info": {
            "type": "object",
            "properties": {
                "goal_name": {"type": "string"},
                "description": {"type": "string"},
                "start_date": {"type": "string", "format": "date"},
                "target_completion_date": {"type": "string", "format": "date"},
                "category": {"type": "string"},
                "success_criteria": {"type": "string"},
                "status": {"type": "string"},
                "level": {"type": "string"},
                "subtype": {"type": "string"}
            },
            "required": ["goal_name", "description", "start_date", "target_completion_date", "category", "success_criteria", "status", "level", "subtype"]
        },
        "measurements": {
            "type": "array",  # Define measurements as an array
            "items": {  # Each item in the array should be an object with the following structure
                "type": "object",
                "properties": {
                    "measurement_name": {"type": "string"},
                    "unit_of_measure": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "comments": {"type": "string"},
                    "target_type": {"type": "string"},
                    "target_value": {"type": "string"},
                    "actual_value": {"type": "string"}
                },
                "required": ["measurement_name", "unit_of_measure", "start_date", "end_date", "comments", "target_type", "target_value", "actual_value"]
            }
        },
        "tasks": {
            "type": "array",  # Define tasks as an array
            "items": {  # Each item in the array should be an object with the following structure
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "comments": {  # Define comments as an array of strings
                        "type": "array",
                        "items": {"type": "string"}
                    },
                   "completion_percentage": {"type": "string"},
                   "start_date": {"type": "string", "format": "date"},
                   "target_completion_date": {"type": "string", "format": "date"},
                   "related_link": {  # Define related links as an array of URIs
                        "type": "array",
                        "items": {"type": "string", "format": "uri"}
                    }
               },
           "required": ["name", "type", "status", "priority", "completion_percentage", "start_date", "target_completion_date"]  # Optional fields are not required
            }
        }
    },
    "required": ["basic_info", "measurements", "tasks"]#"eligibility_profiles"]
}

# HR or Manager Route to Create a New Goal
# This route allows HR or managers to create a new goal in the `goals_collection`.
# 1. The input data is validated against a predefined schema (`goal_schema`).
#    - If the data doesn't conform to the schema, a validation error is returned.
# 2. Before creating a new goal, the route checks if a goal with the same `goal_name` already exists in the collection.
#    - If such a goal exists, a conflict error (409) is returned.
# 3. If the goal does not exist, a new goal is created with the current timestamp (`updated_at`) and the person who created it (`updated_by`).
# 4. The newly created goal is inserted into the `goals_collection`, and its details, including the newly generated ID, are returned in the response.
# 5. The response confirms the creation of the goal with a status of 201 (Created).
@goal_bp.route('/create', methods=['POST'])
def create_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Validate input JSON against the schema
    try:
        validate(instance=data, schema=goal_schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid input data", "message": str(e)}), 400


    # Check if the goal with the same name already exists
    existing_goal = goals_collection.find_one({
    "basic_info.goal_name": data['basic_info']['goal_name']
})
    
    if existing_goal:
        return jsonify({"error": "A goal with this name already exists."}), 409

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")

    data["updated_by"] = updated_by
    data["updated_at"] = current_time

    # Insert the new goal into the goals collection
    goal_id = goals_collection.insert_one(data).inserted_id
    new_goal = goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])

    return jsonify(new_goal), 201

# HR + Manager Route to Assign a Goal to an Individual Employee(`my_goals_collection`)
# This endpoint allows assigning a goal to an individual employee based on the following logic:
# 1. The goal must already exist in the `goal_collection` before assigning.
# 2. Optionally, comments for the goal can be added. If missing, this can be added through another route.
# 3. The goal can be aligned with a goal plan if needed; otherwise, it can be assigned without a goal plan.
#    3.1 If a goal is assigned with a goal plan, the employee must be eligible for the plan.
# 4. Measurements, tasks, and other goal-related attributes can be customized when assigning the goal.
#    If not provided, default values from the `goal_collection` will be used.
# 5. Managers or HR can update fields, add measurements, tasks, comments, or change the start date or target completion date
#    using another route. They can filter based on employee, goal plan, or any other relevant attributes for updating.
@goal_bp.route('/assign', methods=['POST'])
def add_goal():
    data = lowercase_keys(request.json)
    required_fields = ["person_name", "goal_name", "goal_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400
    
    worker_exists = employee_details_collection.find_one({'person_name': data.get("person_name")})
    if worker_exists:
      print("exist")
    else:
     return jsonify({"error": "Person name not exist"}), 400

    goal1 = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal1:
        return jsonify({"error": "goal not found in goal collection"}), 404 

    if (data.get('goal_plan_name') and data.get('review_period') and data.get('performance_document_type')):
        goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name'),
                                                  "details.review_period": data.get('review_period'),
                                                  "details.performance_document_type": data.get('performance_document_type')})
        if not goal_plan1:    
           return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404
        # Fetching the goal plan document based on the goal plan name
        
    
        eligibility_profile_names = [profile["name"] for profile in goal_plan1.get("eligibility_profiles", [])]
        included_workers = set(goal_plan1.get("included_workers", []))
        excluded_workers = set(goal_plan1.get("excluded_workers", []))
    
        eligibility_profiles = []
        combined_employees = set()

        for profile_name in eligibility_profile_names:
          profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
          if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligible_employees = set(get_matching_employees(profile_data))
            eligibility_profiles.append({
                "name": profile_data["eligibility_profile_definition"]["name"],
                "employees_name": list(eligible_employees)  # Fetch and include only the employees matching this profile
            })
            combined_employees.update(eligible_employees)
          else:
            print(f"Profile not found: {profile_name}")


        # First, validate included workers against the employee collection
        validated_included_workers = set()
        for worker in included_workers:
       # Check if the worker exists in either the employee collection
         worker_exists = employee_details_collection.find_one({'person_name': worker})
         if worker_exists:
            validated_included_workers.add(worker)
         else:
            print(f"Excluded worker not found in collections: {worker}")

        # Combine all eligible employees with validated included workers, then subtract excluded workers
        combined_employees.update(validated_included_workers)
        combined_employees.difference_update(excluded_workers)
        def is_person_in_combined_employees(person_name, combined_employees):
            return person_name in combined_employees

        if not is_person_in_combined_employees(data.get('person_name'), combined_employees):
            return jsonify({"error": "person not eligible for this goal_plan."}) 
    else:
        if (data.get('goal_plan_name') or data.get('review_period') or data.get('performance_document_type')):
          return jsonify({"error": "Please provide either all details (goal_plan_name, review_period, performance_document_type) or none of them."})
    
    updated_by = data.get('updated_by', 'Admin')
    goal_type = data.get('goal_type')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Define allowed fields for measurements
    allowed_measurement_fields = {
    "measurement_name",
    "unit_of_measure",
    "start_date",
    "end_date",
    "comments",
    "target_type",
    "target_value",
    "actual_value"
    }

    # Validate and filter measurement fields
    if data.get('measurements', {}):
       measurements1 = []
       for measurement in data.get('measurements'):
           # Check if any required fields are missing
            missing_measurement_fields = [field for field in allowed_measurement_fields if field not in measurement]
            if missing_measurement_fields:
                return jsonify({"error": "Missing fields in measurement", "missing": missing_measurement_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in measurement if field not in allowed_measurement_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in measurement", "extra_fields": extra_fields}), 400
            measurements1.append(measurement)
        # # Filter measurement fields to only include allowed ones
        #  filtered_measurement = {key: value for key, value in measurement.items() if key in allowed_measurement_fields}
        #  measurements1.append(filtered_measurement)
    else:
      measurements1 = goal1.get("measurements",[])

    # Define allowed fields for tasks (if you also want to restrict fields for tasks)
    allowed_task_fields = {
    "name",
    "type",
    "status",
    "priority",
    "comments",
    "completion_percentage",
    "start_date",
    "target_completion_date",
    "related_link"
    }

    # Validate and filter task fields
    if data.get('tasks', {}):
       tasks1 = []
       for task in data.get('tasks'):
           # Check if any required fields are missing
            missing_task_fields = [field for field in allowed_task_fields if field not in task]
            if missing_task_fields:
                return jsonify({"error": "Missing fields in task", "missing": missing_task_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in task if field not in allowed_task_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in task", "extra_fields": extra_fields}), 400

            tasks1.append(task)           
        # # Filter task fields to only include allowed ones
        #  filtered_task = {key: value for key, value in task.items() if key in allowed_task_fields}
        #  tasks1.append(filtered_task)
    else:
      tasks1 = goal1.get("tasks",[])

    if data.get('start_date'):
       start_date1=data.get('start_date')
    else:start_date1=goal1['basic_info'].get('start_date')

    if data.get('target_completion_date'):
       target_completion_date1=data.get('target_completion_date')
    else:target_completion_date1=goal1['basic_info'].get('target_completion_date')    


    # Check if any goal with the same person_name and goal_name exists, sorted by target_completion_date in descending order
    existing_goal = my_goals_collection.find_one(
        {
            "person_name": data.get("person_name"),
            "goal_name": data.get("goal_name")
        },
        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
    )

    if existing_goal:
        # Compare the target_completion_date of the existing goal with the new start_date
        existing_target_completion_date = existing_goal.get("target_completion_date")
        
        # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
        existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
        new_start_date = datetime.strptime(start_date1, '%Y-%m-%d')

        if existing_target_completion_date >= new_start_date:
            return jsonify({"error": "goal already assigned."}), 400
        # If the target_completion_date is less than the new start_date, allow the new goal to be assigned

    goal_data = {
        "person_name": data.get("person_name"),
        "goal_plan_assigned": data.get('goal_plan_name','N/A'),
        "review_period":data.get('review_period','N/A'),
        "performance_document_type":data.get('performance_document_type','N/A'),
        "goal_name": data.get("goal_name"),
        "start_date":start_date1,
        "target_completion_date": target_completion_date1,
        "goal_type": goal_type,
        "progress": data.get("progress", "Not started"),
        "measurements": measurements1,
        "tasks": tasks1,
        "comments": data.get("comments", []),
        "feedback": data.get("feedback", []),
        "updated_by": updated_by,
        "updated_at": current_time
    }
     
    # Insert the goal into the my_goals collection
    goal_id = my_goals_collection.insert_one(goal_data).inserted_id
    # send_email_on_goal_assignment(goal_data)
    new_goal = my_goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    return jsonify(new_goal), 201

# Employee Goal Request Route
# This endpoint allows an employee to request a goal assignment, which then goes for approval by a manager or HR.
# 1. The goal must already exist in the `goal_collection` before the employee can request it.
# 2. The employee can use this route to request a goal for themselves, and the request goes to the manager or HR.
#    This request is recorded in the `goal_offering_collection`. If the status is approved by the manager or HR,
#    the goal is automatically assigned to the employee and added to the c. 
#    If the request is rejected, the goal is not assigned.
# 3. If the employee requests a goal with a goal plan:
#    - The employee must be eligible for that goal plan. If the employee is not eligible, the request will not proceed, 
#      and an error will be returned without the request being sent to the manager or HR.
#    - If the employee is eligible, the request will be sent for approval as usual.
#    - otherwise, it can be assigned without a goal plan.
# goal offering
@goal_bp.route('/goal_offering', methods=['POST'])
def goal_offering():
    data = lowercase_keys(request.json)
    # Validate necessary fields are present
    if 'person_name' not in data or 'goal_name' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    worker_exists = employee_details_collection.find_one({'person_name': data.get("person_name")})
    if worker_exists:
      print("exist")
    else:
     return jsonify({"error": "Person name not exist"}), 400
    
    goal = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal:
        return jsonify({"error": "goal not found in goal collection"}), 404 

    if (data.get('goal_plan_name') and data.get('review_period') and data.get('performance_document_type')):
        goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name'),
                                                  "details.review_period": data.get('review_period'),
                                                  "details.performance_document_type": data.get('performance_document_type')})
        if not goal_plan1:    
           return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404
        
    
        eligibility_profile_names = [profile["name"] for profile in goal_plan1.get("eligibility_profiles", [])]
        included_workers = set(goal_plan1.get("included_workers", []))
        excluded_workers = set(goal_plan1.get("excluded_workers", []))
    
        eligibility_profiles = []
        combined_employees = set()

        for profile_name in eligibility_profile_names:
          profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
          if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligible_employees = set(get_matching_employees(profile_data))
            eligibility_profiles.append({
                "name": profile_data["eligibility_profile_definition"]["name"],
                "employees_name": list(eligible_employees)  # Fetch and include only the employees matching this profile
            })
            combined_employees.update(eligible_employees)
          else:
            print(f"Profile not found: {profile_name}")


        # First, validate included workers against the employee collection
        validated_included_workers = set()
        for worker in included_workers:
       # Check if the worker exists in either the employee collection
         worker_exists = employee_details_collection.find_one({'person_name': worker})
         if worker_exists:
            validated_included_workers.add(worker)
         else:
            print(f"Excluded worker not found in collections: {worker}")

        # Combine all eligible employees with validated included workers, then subtract excluded workers
        combined_employees.update(validated_included_workers)
        combined_employees.difference_update(excluded_workers)
        def is_person_in_combined_employees(person_name, combined_employees):
            return person_name in combined_employees

        if not is_person_in_combined_employees(data.get('person_name'), combined_employees):
            return jsonify({"error": "person not eligible for this goal_plan."}) 
     
    else:
        if (data.get('goal_plan_name') or data.get('review_period') or data.get('performance_document_type')):
          return jsonify({"error": "Please provide either all details (goal_plan_name, review_period, performance_document_type) or none of them."})
    

    # Define allowed fields for measurements
    allowed_measurement_fields = {
    "measurement_name",
    "unit_of_measure",
    "start_date",
    "end_date",
    "comments",
    "target_type",
    "target_value",
    "actual_value"
    }

    # Validate and filter measurement fields
    if data.get('measurements', {}):
       measurements1 = []
       for measurement in data.get('measurements'):
        # Check if any required fields are missing
            missing_measurement_fields = [field for field in allowed_measurement_fields if field not in measurement]
            if missing_measurement_fields:
                return jsonify({"error": "Missing fields in measurement", "missing": missing_measurement_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in measurement if field not in allowed_measurement_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in measurement", "extra_fields": extra_fields}), 400

            measurements1.append(measurement)
    else:
      measurements1 = goal.get("measurements",[])

    # Define allowed fields for tasks (if you also want to restrict fields for tasks)
    allowed_task_fields = {
    "name",
    "type",
    "status",
    "priority",
    "comments",
    "completion_percentage",
    "start_date",
    "target_completion_date",
    "related_link"
    }

    # Validate and filter task fields
    if data.get('tasks', {}):
       tasks1 = []
       for task in data.get('tasks'):
            # Check if any required fields are missing
            missing_task_fields = [field for field in allowed_task_fields if field not in task]
            if missing_task_fields:
                return jsonify({"error": "Missing fields in task", "missing": missing_task_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in task if field not in allowed_task_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in task", "extra_fields": extra_fields}), 400

            tasks1.append(task)
    else:
      tasks1 = goal.get("tasks",[])

    if data.get('start_date'):
       start_date1=data.get('start_date')
    else:start_date1=goal['basic_info'].get('start_date')

    if data.get('target_completion_date'):
       target_completion_date1=data.get('target_completion_date')
    else:target_completion_date1=goal['basic_info'].get('target_completion_date')

    existing_goal1 = my_goals_collection.find_one(
        {
            "person_name": data.get("person_name"),
            "goal_name": data.get("goal_name")
        },
        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
    )

    if existing_goal1:
        # Compare the target_completion_date of the existing goal with the new start_date
        existing_target_completion_date1 = existing_goal1.get("target_completion_date")
        
        # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
        existing_target_completion_date1 = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
        new_start_date1 = datetime.strptime(start_date1, '%Y-%m-%d')

        if existing_target_completion_date1 >= new_start_date1:
            return jsonify({"error": "goal already assigned."}), 400
        # If the target_completion_date is less than the new start_date, allow the new goal to be assigned



    existing_goal = goal_offering_collection.find_one(
        {
            "person_name": data.get("person_name"),
            "goal_name": data.get("goal_name"),
            "status": "approval_required"
        },
        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
    )

    if existing_goal:
        # Compare the target_completion_date of the existing goal with the new start_date
        existing_target_completion_date = existing_goal.get("target_completion_date")
        
        # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
        existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
        new_start_date = datetime.strptime(start_date1, '%Y-%m-%d')

        if existing_target_completion_date >= new_start_date:
            return jsonify({"error": "goal already exists."}), 400
        # If the target_completion_date is less than the new start_date, allow the new goal to be assigned

    # Prepare the goal data
    goal_data = {
        "person_name": data.get("person_name"),
        "goal_plan_assigned": data.get("goal_plan_name","N/A"),
        "review_period":data.get('review_period','N/A'),
        "performance_document_type":data.get('performance_document_type','N/A'),
        "goal_name": data.get("goal_name"),
        "start_date":start_date1,
        "target_completion_date": target_completion_date1,
        "measurements": measurements1,
        "tasks": tasks1,
        "status": "approval_required",
        "timestamp": current_time
    }
    
    
    # Insert the goal into the my_goals collection
    goal_id = goal_offering_collection.insert_one(goal_data).inserted_id
    new_goal = goal_offering_collection.find_one({'_id': goal_id})
    send_email_on_goal_offering(new_goal)
    new_goal['_id'] = str(new_goal['_id'])
    
    return jsonify(new_goal), 201

# Manager/HR Goal Request Processing Route
# This endpoint allows a manager or HR to process the goal requests made by employees.
# It is used to either approve or reject the goal request that an employee submitted through the `/goal_offering` route.
@goal_bp.route('/process_goal', methods=['POST'])
def process_goal():
    data = lowercase_keys(request.json)
    if 'person_name' not in data or 'goal_name' not in data or 'status' not in data or 'goal_plan_assigned' not in data or 'review_period' not in data or 'performance_document_type' not in data :
     return jsonify({"error": "Missing required fields"}), 400
    
    updated_by = data.get('updated_by', 'Admin')
    goal_type = data.get('goal_type','development')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    person_name = data.get("person_name")
    goal_name = data.get("goal_name")
    status = data.get("status")
    goal_plan_assigned= data.get("goal_plan_assigned")
    review_period= data.get("review_period")
    performance_document_type= data.get("performance_document_type")
    
    if status not in ["approved", "rejected"]:#, "changes_requested"]:
        return jsonify({"error": "Invalid status"}), 400
    
    goal = goal_offering_collection.find_one(
        {
            "person_name": data.get("person_name"),
            "goal_name": data.get("goal_name"),
            "status": "approval_required"
        },
        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
    )

    if not goal:
       return jsonify({"error": "Goal not found"}), 404
 
    # if status == "changes_requested":
    #  goal_offering_collection.update_one(
    #     {
    #         "person_name": person_name,
    #         "goal_name": goal_name
    #     },
    #     {'$set': {
    #               "changes_request": change_request}}
    # )   

    # data['status'] = status

    # goal_offering_collection.update_one(
    #     {
    #         "person_name": person_name,
    #         "goal_name": goal_name
    #     },
    #     {'$set': {"status": status,
    #               "timestamp":current_time}}
    # )

    
    # goal1 = goals_collection.find_one({"basic_info.goal_name": goal_name})

    # Check if any goal with the same person_name and goal_name exists, sorted by target_completion_date in descending order
    existing_goal = my_goals_collection.find_one(
        {
            "person_name": data.get("person_name"),
            "goal_name": data.get("goal_name")
        },
        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
    )

    if existing_goal:
        # Compare the target_completion_date of the existing goal with the new start_date
        existing_target_completion_date = existing_goal.get("target_completion_date")
        
        # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
        existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
        new_start_date = datetime.strptime(goal["start_date"], '%Y-%m-%d')

        if existing_target_completion_date >= new_start_date:
            return jsonify({"error": "goal already assigned."}), 400
        # If the target_completion_date is less than the new start_date, allow the new goal to be assigned

 
    if status == "approved":
        # Move the goal to the my goals collection
        my_goals_collection.insert_one({
            "person_name": goal["person_name"],
            "goal_plan_assigned": goal["goal_plan_assigned"],
            "review_period":review_period,
            "performance_document_type":performance_document_type,
            "goal_name": goal["goal_name"],
            "start_date":goal["start_date"],
            "target_completion_date": goal["target_completion_date"],
            "goal_type": goal_type,
            "progress": "Not started",
            "measurement": goal["measurements"],
            "tasks": goal["tasks"],
            "comments": [],
            "feedback": [],
            "updated_by": updated_by,
            "updated_at": current_time
        })
        goal_offering_collection.update_one(
            {
                goal
                # "person_name": person_name,
                # "goal_name": goal_name,
                # "goal_plan_assigned": goal_plan_assigned,
                # "review_period":review_period,
                # "performance_document_type":performance_document_type
            },
           
            {'$set': {"status": "approved",
                       "timestamp":current_time}}
        )
    else:
        # Update the status of the goal to "rejected" in the goal offering collection
        goal_offering_collection.update_one(
            {
                goal
                # "person_name": person_name,
                # "goal_name": goal_name,
                # "goal_plan_assigned": goal_plan_assigned,
                # "review_period":review_period,
                # "performance_document_type":performance_document_type
            },
            {'$set': {"status": "rejected",
                      "timestamp":current_time}}
        )

    return jsonify({"message": "Goal processed", "person_name": person_name, "goal_name": goal_name, "status": status}), 200

# HR or Manager Route to Mass Assign a Goal to Multiple Employees Based on Eligibility Profiles
# This route allows HR or managers to assign a goal to a group of employees based on eligibility profiles.(`my_goals_collection`)
# 1. If a goal plan is provided:
#    1.1 Employees must be eligible for the provided goal plan, and their eligibility is validated against the provided eligibility profiles.
#    1.2 If the employees are not eligible for the goal plan, the goal will not be assigned.
# 2. If no goal plan is provided, the goal is assigned to employees based on the specified eligibility profiles alone.
# 3. Other details such as measurements, start date, target completion date, and other task-related information 
#    follow the same rules as discussed for the individual goal assignment route.
@goal_bp.route('/mass_assign', methods=['POST'])
def assign_goal_to_all_employees():
    data = lowercase_keys(request.json)
    if 'goal_type' not in data or 'eligibility_profiles' not in data or 'goal_name' not in data or 'included_workers' not in data or 'excluded_workers' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Ensure that eligibility_name can handle multiple profiles
    eligibility_names = data.get("eligibility_profiles", [])
    if isinstance(eligibility_names, str):
        eligibility_names = [eligibility_names]  # Convert to list if a single string is provided
    
    combined_employees = set()

    eligibility_profilesg = []
    combined_employeesg = set()

    for eligibility_name in eligibility_names:
        eligibility_profile = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": eligibility_name})
        
        if not eligibility_profile:
            return jsonify({"error": f"eligibility not found in eligibility collection: {eligibility_name}"}), 404 
        
        # Fetch and match employees based on eligibility criteria
        eligible_employees = set(get_matching_employees(eligibility_profile))
        # print(f"Eligible employees for {eligibility_name}: {eligible_employees}")
        combined_employees.update(eligible_employees)

    # Check if the goal exists in goals_collection
    goal1 = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal1:
        return jsonify({"error": "goal not found in goal collection"}), 404 

    # Check if the goal_plan exists in goal_plan_collection
    if (data.get('goal_plan_name') and data.get('review_period') and data.get('performance_document_type')):
        goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name'),
                                                     "details.review_period": data.get('review_period'),
                                                     "details.performance_document_type": data.get('performance_document_type')})
        if not goal_plan1:    
           return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404
            
        eligibility_profile_namesg = [profile["name"] for profile in goal_plan1.get("eligibility_profiles", [])]
        included_workersg = set(goal_plan1.get("included_workers", []))
        excluded_workersg = set(goal_plan1.get("excluded_workers", []))
    

        for profile_name in eligibility_profile_namesg:
          profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
          if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligible_employeesg = set(get_matching_employees(profile_data))
            eligibility_profilesg.append({
                "name": profile_data["eligibility_profile_definition"]["name"],
                "employees_name": list(eligible_employees)  # Fetch and include only the employees matching this profile
            })
            combined_employeesg.update(eligible_employeesg)
          else:
            print(f"Profile not found: {profile_name}")


        # First, validate included workers against the employee collection
        validated_included_workersg = set()
        for worker in included_workersg:
       # Check if the worker exists in either the employee collection
         worker_exists = employee_details_collection.find_one({'person_name': worker})
         if worker_exists:
            validated_included_workersg.add(worker)
         else:
            print(f"Excluded worker not found in collections: {worker}")

        # Combine all eligible employees with validated included workers, then subtract excluded workers
        combined_employeesg.update(validated_included_workersg)
        combined_employeesg.difference_update(excluded_workersg)
    else:
        if (data.get('goal_plan_name') or data.get('review_period') or data.get('performance_document_type')):
          return jsonify({"error": "Please provide either all details (goal_plan_name, review_period, performance_document_type) or none of them."})
    
    # Define allowed fields for measurements
    allowed_measurement_fields = {
    "measurement_name",
    "unit_of_measure",
    "start_date",
    "end_date",
    "comments",
    "target_type",
    "target_value",
    "actual_value"
    }

    # Validate and filter measurement fields
    if data.get('measurements', {}):
       measurements1 = []
       for measurement in data.get('measurements'):
        # Check if any required fields are missing
            missing_measurement_fields = [field for field in allowed_measurement_fields if field not in measurement]
            if missing_measurement_fields:
                return jsonify({"error": "Missing fields in measurement", "missing": missing_measurement_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in measurement if field not in allowed_measurement_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in measurement", "extra_fields": extra_fields}), 400

            measurements1.append(measurement)
    else:
      measurements1 = goal1.get("measurements",[])

    # Define allowed fields for tasks (if you also want to restrict fields for tasks)
    allowed_task_fields = {
    "name",
    "type",
    "status",
    "priority",
    "comments",
    "completion_percentage",
    "start_date",
    "target_completion_date",
    "related_link"
    }

    # Validate and filter task fields
    if data.get('tasks', {}):
       tasks1 = []
       for task in data.get('tasks'):
        # Check if any required fields are missing
            missing_task_fields = [field for field in allowed_task_fields if field not in task]
            if missing_task_fields:
                return jsonify({"error": "Missing fields in task", "missing": missing_task_fields}), 400

            # Check for any extra fields
            extra_fields = [field for field in task if field not in allowed_task_fields]
            if extra_fields:
                return jsonify({"error": "Extra fields in task", "extra_fields": extra_fields}), 400

            tasks1.append(task)
    else:
      tasks1 = goal1.get("tasks",[])


    if data.get('start_date'):
       start_date1=data.get('start_date')
    else:start_date1=goal1['basic_info'].get('start_date')

    if data.get('target_completion_date'):
       target_completion_date1=data.get('target_completion_date')
    else:target_completion_date1=goal1['basic_info'].get('target_completion_date')


    # Handle included and excluded workers
    included_workers = set(data.get("included_workers", []))
    excluded_workers = set(data.get("excluded_workers", []))

    # Validate included workers against employee collection
    validated_included_workers = set()
    for worker in included_workers:
        # Check if the worker exists in the employee collection
        worker_exists = employee_details_collection.find_one({'person_name': worker})
        if worker_exists:
            validated_included_workers.add(worker)
        else:
            print(f"Included worker not found in collections: {worker}")

    # Combine all eligible employees with validated included workers, then subtract excluded workers
    combined_employees.update(validated_included_workers)
    combined_employees.difference_update(excluded_workers)
    if combined_employeesg:
     combined_employees=combined_employees.intersection(combined_employeesg)

    updated_by = data.get('updated_by', 'Admin')
    goal = data.get('goal_name')
    goal_type = data.get('goal_type')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    my_goals_entries = []
    for employee_name in combined_employees:
        # Check if any goal with the same person_name and goal_name exists, sorted by target_completion_date in descending order
        existing_goal = my_goals_collection.find_one(
            {
                "person_name": employee_name,
                "goal_name": goal
            },
            sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
        )

        if existing_goal:
            # Compare the target_completion_date of the existing goal with the new start_date
            existing_target_completion_date = existing_goal.get("target_completion_date")
            
            # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
            existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
            new_start_date = datetime.strptime(start_date1, '%Y-%m-%d')

            if existing_target_completion_date >= new_start_date:
                continue
                # return jsonify({"error": "goal already assigned."}), 400
            # If the target_completion_date is less than the new start_date, allow the new goal to be assigned

    #     existing_goal = my_goals_collection.find_one({
    #     "person_name": employee_name,
    #     "goal_name": goal,
    #     "start_date": start_date1,
    #     "target_completion_date": target_completion_date1
    # })
    
    #     if existing_goal:
    #         continue
    #     #  return jsonify({"error": "This goal already exists for the specified person with the same start and target completion dates","person_name": employee_name}), 400

        my_goals_entry = {
            "person_name": employee_name,
            "goal_plan_assigned": data.get('goal_plan_name','N/A'),
            "review_period":data.get('review_period','N/A'),
            "performance_document_type":data.get('performance_document_type','N/A'),
            "goal_name": goal,
            "start_date":start_date1,
            "target_completion_date": target_completion_date1,
            "goal_type": goal_type,
            "progress": data.get('progress', 'Not started'),  # Default value
            "measurements": measurements1,
            "tasks": tasks1,
            "comments": data.get('comments',[]),
            "feedback": [],
            "updated_by": updated_by,
            "updated_at": current_time
        }
        my_goals_entries.append(my_goals_entry)
        send_email_on_goal_assignment(my_goals_entry)

    if my_goals_entries:
        result = my_goals_collection.insert_many(my_goals_entries)
    else:  return jsonify({'message': 'Goals already assigned'}), 200     


# Prepare the assignment data for the PGM_assign_oras_goals collection
    assignment_data = {
            "process": "mass assign goal",
            "goal_plan_name": data.get('goal_plan_name','N/A'),
            "review_period": data.get('review_period','N/A'),
            "performance_document_type":data.get('performance_document_type','N/A'),
            "goals":goal,
            "eligibility_profiles":eligibility_names,
            "included_workers":data.get("included_workers", []),
            "excluded_workers": data.get("excluded_workers", []),
            "updated_by": data.get('updated_by', 'Admin'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Insert assignment data into the PGM_assign_oras_goals collection
    result = mass_assign.insert_one(assignment_data)


    return jsonify({'message': 'Goals successfully assigned'}), 200

# HR or Manager Route to Assign Goals from a Goal Plan to Eligible Employees(`my_goals_collection`)
# This route is used by HR or managers to assign all goals present in a specific goal plan to eligible employees.
# 1. The employees eligible for the goal plan are determined based on the eligibility profiles associated with the plan.
#    - If a goal plan is provided, employees must meet the eligibility criteria defined in the goal plan.
# 2. Included workers (who are explicitly part of the goal plan) will also be considered, while excluded workers will be removed from the list.
# 3. The goals from the goal plan will be assigned to the eligible employees, along with related information like measurements, tasks, 
#    start date, and target completion date from the goal details stored in the `goals_collection`.
# 4. Each eligible employee will have the goals assigned to them, and this data will be stored in the `my_goals_collection`.
@goal_bp.route('/assign_on_combined_employee_list', methods=['POST'])
def fetch_goals():
    data = lowercase_keys(request.json)
    if 'goal_plan_name' not in data or 'review_period' not in data or 'performance_document_type' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    goal_type = data.get('goal_type','performance')
    updated_by = data.get('updated_by', 'Admin')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Fetching the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": data.get('goal_plan_name'),
                                                "details.review_period": data.get('review_period'),
                                                "details.performance_document_type": data.get('performance_document_type')})

    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404
    
    eligibility_profile_names = [profile["name"] for profile in goal_plan.get("eligibility_profiles", [])]
    included_workers = set(goal_plan.get("included_workers", []))
    excluded_workers = set(goal_plan.get("excluded_workers", []))
    
    eligibility_profiles = []
    combined_employees = set()

    for profile_name in eligibility_profile_names:
        profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
        if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligible_employees = set(get_matching_employees(profile_data))
            eligibility_profiles.append({
                "name": profile_data["eligibility_profile_definition"]["name"],
                "employees_name": list(eligible_employees)  # Fetch and include only the employees matching this profile
            })
            combined_employees.update(eligible_employees)
        else:
            print(f"Profile not found: {profile_name}")


    # First, validate included workers against the employee collection
    validated_included_workers = set()
    for worker in included_workers:
    # Check if the worker exists in either the employee collection
      worker_exists = employee_details_collection.find_one({'person_name': worker})
      if worker_exists:
        validated_included_workers.add(worker)
      else:
        print(f"Excluded worker not found in collections: {worker}")

     # Combine all eligible employees with validated included workers, then subtract excluded workers
    combined_employees.update(validated_included_workers)
    combined_employees.difference_update(excluded_workers)

    # Retrieve the goal names
    goals = goal_plan.get('goals', [])

    # Check if goals are present in the goal plan
    if not goals:
        return jsonify({'error': 'No goals found in the goal plan. Cannot assign goals to employees.'}), 400

    # Creating my_goals collection entries
    my_goals_entries = []
    for employee_name in combined_employees:
        for goal_name in goals:
            # Fetch the full goal details from the goals collection
            goal = goals_collection.find_one({"basic_info.goal_name": goal_name})
            if not goal:
                print(f"Goal not found in goals collection for goal name: {goal_name}")
                continue  # Skip if the goal is not found
            else:
                measurements1=goal.get("measurements")
                tasks1=goal.get("tasks")
            # Include measurement details from the goal
       
            # Check if any goal with the same person_name and goal_name exists, sorted by target_completion_date in descending order
            existing_goal = my_goals_collection.find_one(
                {
                    "person_name": employee_name,
                    "goal_name": goal_name
                },
                sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
            )

            if existing_goal:
                # Compare the target_completion_date of the existing goal with the new start_date
                existing_target_completion_date = existing_goal.get("target_completion_date")
                
                # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
                existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
                new_start_date = datetime.strptime(goal['basic_info'].get('start_date'), '%Y-%m-%d')

                if existing_target_completion_date >= new_start_date:
                    continue
                    # return jsonify({"error": "goal already assigned."}), 400
                # If the target_completion_date is less than the new start_date, allow the new goal to be assigned



            # existing_goal = my_goals_collection.find_one({
            #  "person_name": employee_name,
            #   "goal_name": goal_name,
            #   "start_date": goal['basic_info'].get('start_date'),
            #   "target_completion_date": goal['basic_info'].get('target_completion_date')
            # })
    
            # if existing_goal:
            #    continue
            # #    return jsonify({"error": "goal already exists for the specified person with the same start and target completion dates","person_name": employee_name,"goal_name":goal_name}), 400

            my_goals_entry = {
                "person_name": employee_name,
                "goal_plan_assigned": data.get('goal_plan_name'),
                "review_period":data.get('review_period'),
                "performance_document_type":data.get('performance_document_type'),
                "goal_name": goal_name,
                "start_date":goal['basic_info'].get('start_date'),
                "target_completion_date":goal['basic_info'].get('target_completion_date'),
                "goal_type": goal_type,
                "progress": data.get('progress', 'Not started'),  # Default value
                "measurements": measurements1,  # Include the measurement from the goal
                "tasks": tasks1,
                "comments": [],
                "feedback": [],
                "updated_by": updated_by,
                "updated_at": current_time
            }
           
            my_goals_entries.append(my_goals_entry)
            send_email_on_goal_assignment(my_goals_entry)

    # Insert into my_goals collection
    if my_goals_entries:
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))
    else:  return jsonify({'message': 'Goals already assigned'}), 200   
    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])

    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200

# HR or Manager Route to Assign Goals to Employees Based on Goal Plan and Eligibility Profiles(`my_goals_collection`)
# This route is used to assign specific goals to employees who meet the eligibility criteria provided in the goal plan and eligibility profiles provided here.
# 1. The goal plan is provided along with eligibility profiles, and employees must be eligible for both the goal plan and the eligibility profiles.
# 2. If employees are eligible, goals are assigned to them. If no goal details are provided, the system fetches default details from the `goals_collection`.
# 3. The route handles goal assignment based on the provided goal details (if available), such as measurements, tasks, start date, target completion date, and comments.
#    If these details are not provided, they are fetched from the goal details stored in the `goals_collection`.
# 4. Included workers are validated and excluded workers are removed from the assignment list.
@goal_bp.route('/assign_goals', methods=['POST'])
def assign_goals():
    try:
        # Get inputs from request
        data = lowercase_keys(request.json)
        if 'goal_plan_name' not in data or 'goals' not in data or 'review_period' not in data or 'performance_document_type' not in data or 'eligibility_profiles' not in data or 'included_workers' not in data or 'excluded_workers' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        goal_plan_name = data.get('goal_plan_name')
        review_period = data.get('review_period')
        performance_document_type = data.get('performance_document_type')

        eligibility_names = data.get("eligibility_profiles", [])
        if isinstance(eligibility_names, str):
            eligibility_names = [eligibility_names]  # Convert to list if a single string is provided

        combined_employees = set()

        for eligibility_name in eligibility_names:
            eligibility_profile = eligibility_profiles_collection.find_one(
                {"eligibility_profile_definition.name": eligibility_name})
            if not eligibility_profile:
                return jsonify({"error": f"eligibility not found in eligibility collection: {eligibility_name}"}), 404

            # Fetch and match employees based on eligibility criteria
            eligible_employees = set(get_matching_employees(eligibility_profile))
            combined_employees.update(eligible_employees)
        

        included_workers = set(data.get("included_workers", []))
        excluded_workers = set(data.get("excluded_workers", []))

        validated_included_workers = set()
        for worker in included_workers:
            worker_exists = employee_details_collection.find_one({'person_name': worker})
            if worker_exists:
                validated_included_workers.add(worker)
            else:
                print(f"Excluded worker not found in collections: {worker}")

        # Combine all eligible employees with validated included workers, then subtract excluded workers
        combined_employees.update(validated_included_workers)
        combined_employees.difference_update(excluded_workers)
      


        # Fetch goal plan details
        goal_plan = goal_plan_collection.find_one({
            "details.goal_plan_name": goal_plan_name,
            "details.review_period": review_period,
            "details.performance_document_type": performance_document_type
        })
        if not goal_plan:
            return jsonify({"error": "Goal plan not found"}), 404

        eligibility_profile_namesg = [profile["name"] for profile in goal_plan.get("eligibility_profiles", [])]
        included_workersg = set(goal_plan.get("included_workers", []))
        excluded_workersg = set(goal_plan.get("excluded_workers", []))

        eligibility_profilesg = []
        combined_employeesg = set()

        for profile_name in eligibility_profile_namesg:
            profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
            if profile_data:
                profile_data['_id'] = str(profile_data['_id'])
                eligible_employeesg = set(get_matching_employees(profile_data))
                eligibility_profilesg.append({
                    "name": profile_data["eligibility_profile_definition"]["name"],
                    "employees_name": list(eligible_employeesg)  # Fetch and include only the employees matching this profile
                })
                combined_employeesg.update(eligible_employeesg)
            else:
                print(f"Profile not found: {profile_name}")
        
        # First, validate included workers against the employee collection
        validated_included_workersg = set()
        for worker in included_workersg:
            worker_exists = employee_details_collection.find_one({'person_name': worker})
            if worker_exists:
                validated_included_workersg.add(worker)
            else:
                print(f"Excluded worker not found in collections: {worker}")

        # Combine all eligible employees with validated included workers, then subtract excluded workers
        combined_employeesg.update(validated_included_workersg)
        combined_employeesg.difference_update(excluded_workersg)

        combined_employees = combined_employees.intersection(combined_employeesg)

        # Fetch goals by name to be assigned
        goal_names = data.get("goals", [])
        assigned_goals_with_employees = []

        for goal_name in goal_names:
            goal = goals_collection.find_one({"basic_info.goal_name": goal_name.get('goal_name')})
            if goal:  
                # Safely fetch measurements, tasks, start_date, target_completion_date, and comments      
                # Define allowed fields for measurements
                allowed_measurement_fields = {
                "measurement_name",
                "unit_of_measure",
                "start_date",
                "end_date",
                "comments",
                "target_type",
                "target_value",
                "actual_value"
                }

                # Validate and filter measurement fields
                if goal_name.get('measurements', {}):
                   measurements1 = []
                   for measurement in goal_name.get('measurements'):
                    # Check if any required fields are missing
                    missing_measurement_fields = [field for field in allowed_measurement_fields if field not in measurement]
                    if missing_measurement_fields:
                        return jsonify({"error": "Missing fields in measurement", "missing": missing_measurement_fields}), 400

                    # Check for any extra fields
                    extra_fields = [field for field in measurement if field not in allowed_measurement_fields]
                    if extra_fields:
                        return jsonify({"error": "Extra fields in measurement", "extra_fields": extra_fields}), 400

                    measurements1.append(measurement)
                else:
                   measurements1 = goal.get("measurements",[])

                # Define allowed fields for tasks (if you also want to restrict fields for tasks)
                allowed_task_fields = {
                "name",
                "type",
                "status",
                "priority",
                "comments",
                "completion_percentage",
                "start_date",
                "target_completion_date",
                "related_link"
                }

                # Validate and filter task fields
                if goal_name.get('tasks', {}):
                  tasks1 = []
                  for task in goal_name.get('tasks'):
                    # Check if any required fields are missing
                    missing_task_fields = [field for field in allowed_task_fields if field not in task]
                    if missing_task_fields:
                        return jsonify({"error": "Missing fields in task", "missing": missing_task_fields}), 400

                    # Check for any extra fields
                    extra_fields = [field for field in task if field not in allowed_task_fields]
                    if extra_fields:
                        return jsonify({"error": "Extra fields in task", "extra_fields": extra_fields}), 400

                    tasks1.append(task)
                else:
                  tasks1 = goal.get("tasks",[])

        
                start_date1 = goal_name.get('start_date', goal.get('basic_info', {}).get('start_date', None))
                target_completion_date1 = goal_name.get('target_completion_date', goal.get('basic_info', {}).get('target_completion_date', None))
                comments1 = goal_name.get('comments', [])

                my_goals_entries = []
                for employee_name in combined_employees:

                    # Check if any goal with the same person_name and goal_name exists, sorted by target_completion_date in descending order
                    existing_goal = my_goals_collection.find_one(
                        {
                            "person_name": employee_name,
                            "goal_name": goal['basic_info']['goal_name']
                        },
                        sort=[("target_completion_date", -1)]  # Sort by target_completion_date descending to get the most recent one
                    )

                    if existing_goal:
                        # Compare the target_completion_date of the existing goal with the new start_date
                        existing_target_completion_date = existing_goal.get("target_completion_date")
                        
                        # Convert dates to datetime objects for comparison (assuming they are strings in ISO format)
                        existing_target_completion_date = datetime.strptime(existing_target_completion_date, '%Y-%m-%d')
                        new_start_date = datetime.strptime(start_date1, '%Y-%m-%d')

                        if existing_target_completion_date >= new_start_date:
                            continue
                            # return jsonify({"error": "goal already assigned."}), 400
                        # If the target_completion_date is less than the new start_date, allow the new goal to be assigned



                    # existing_goal = my_goals_collection.find_one({
                    # "person_name": employee_name,
                    # "goal_name": goal['basic_info']['goal_name'],
                    # "start_date": start_date1,
                    # "target_completion_date": target_completion_date1
                    # })
        
                    # if existing_goal:
                    #     continue
                    # #  return jsonify({"error": "This goal already exists for the specified person with the same start and target completion dates","person_name": employee_name}), 400
                        
                    my_goals_entry = {
                        "person_name": employee_name,
                        "goal_plan_assigned": goal_plan_name,
                        "review_period": review_period,
                        "performance_document_type": performance_document_type,
                        "goal_name": goal['basic_info']['goal_name'],
                        "start_date": start_date1,
                        "target_completion_date": target_completion_date1,
                        "goal_type": data.get('goal_type', 'development'),
                        "progress": data.get('progress', 'Not started'),  # Default value
                        "measurements": measurements1,  # Include the measurement from the goal
                        "tasks": tasks1,
                        "comments": comments1,
                        "feedback": [],
                        "updated_by": data.get('updated_by', 'Admin'),
                        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    my_goals_entries.append(my_goals_entry)
                    send_email_on_goal_assignment(my_goals_entry)
                if my_goals_entries:
                    result = my_goals_collection.insert_many(my_goals_entries)
                    assigned_goals_with_employees.append(my_goals_entries)

                else:  return jsonify({'message': 'Goals already assigned'}), 200   
            else: return jsonify({"message": "goal not found in collection","goal_name":goal_name.get('goal_name')}), 404      

        if not assigned_goals_with_employees:
            return jsonify({"message": "No employees matched the criteria"}), 404


        # Prepare the assignment data for the PGM_assign_oras_goals collection
        assignment_data = {
            "process": "mass assign goals",
            "goal_plan_name": goal_plan_name,
            "review_period": review_period,
            "performance_document_type":performance_document_type,
            "goals":goal_names,
            "eligibility_profiles":eligibility_names,
            "included_workers":data.get("included_workers", []),
            "excluded_workers": data.get("excluded_workers", []),
            "updated_by": data.get('updated_by', 'Admin'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Insert assignment data into the PGM_assign_oras_goals collection
        result = mass_assign.insert_one(assignment_data)

        return jsonify({'message': 'Goals successfully assigned'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# HR or Manager Route to Update an Existing Goal in the Collection
# This route is used to update specific fields of an existing goal in the `goals_collection`.
# 1. The goal must already exist in the collection, and the 'goal_name' field is required to identify the goal.
# 2. The route updates only the fields that are provided in the request and already exist in the current document.
#    - Fields in 'basic_info' are updated if present in both the request and the existing goal.
#    - Measurements are updated based on matching 'measurement_name' and only for fields that already exist.
#    - Tasks are updated similarly, based on matching 'name' and only for existing fields.
# 3. The route also allows updating the 'updated_by' field and automatically updates the 'updated_at' timestamp.
# 4. Only specified fields are updated using the `$set` operation to avoid overwriting non-specified data.
@goal_bp.route('/update_goal', methods=['POST'])
def update_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Ensure 'goal_name' is provided in the request
    goal_name1 = data.get('goal_name')
    if not goal_name1:
        return jsonify({"error": "Missing required field: goal_name"}), 400

    # Find the goal by 'goal_name'
    goal = goals_collection.find_one({"basic_info.goal_name": goal_name1})
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    # Prepare update data only for fields present in the incoming request
    update_data = {}

    # Check and update fields in 'basic_info' if they already exist in the document
    if 'basic_info' in data and isinstance(data['basic_info'], dict):
        for key, value in data['basic_info'].items():
            if key in goal['basic_info']:  # Only update if the field already exists
                update_data[f'basic_info.{key}'] = value

    # Check and update fields in 'measurements' by matching on 'measurement_name'
    if 'measurements' in data and isinstance(data['measurements'], list):
        updated_measurements = []
        for new_measurement in data['measurements']:
            for existing_measurement in goal.get('measurements', []):
                if new_measurement.get('measurement_name') == existing_measurement.get('measurement_name'):
                    updated_measurement = existing_measurement.copy()
                    for key, value in new_measurement.items():
                        if key in existing_measurement:  # Only update existing fields
                            updated_measurement[key] = value
                    updated_measurements.append(updated_measurement)
        if updated_measurements:
            update_data['measurements'] = updated_measurements

    # Check and update fields in 'tasks' by matching on 'name'
    if 'tasks' in data and isinstance(data['tasks'], list):
        updated_tasks = []
        for new_task in data['tasks']:
            for existing_task in goal.get('tasks', []):
                if new_task.get('name') == existing_task.get('name'):
                    updated_task = existing_task.copy()
                    for key, value in new_task.items():
                        if key in existing_task:  # Only update existing fields
                            updated_task[key] = value
                    updated_tasks.append(updated_task)
        if updated_tasks:
            update_data['tasks'] = updated_tasks

    # Update 'updated_by' only if provided
    if 'updated_by' in data:
        update_data['updated_by'] = data['updated_by']

    # Always update the 'updated_at' timestamp
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if there's anything to update
    if not update_data:
        return jsonify({"message": "No valid fields to update"}), 400

    # Update the document in the MongoDB collection using $set
    goals_collection.update_one({"basic_info.goal_name": goal_name1}, {"$set": update_data})

    return jsonify({"message": "Goal updated successfully"}), 200

# HR or Manager Route to Add a Measurement to a Goal
# This route allows HR or managers to add a new measurement to a specific goal in the `goals_collection`.
# 1. The `goal_name` is required to identify the goal to which the measurement will be added.
# 2. Measurement data must be provided, including fields like `measurement_name`, `unit_of_measure`, `start_date`, `end_date`, etc.
# 3. The new measurement will be added to the `measurements` array for the goal.
# 4. The `updated_at` field will be automatically set to the current date and time after the measurement is added.
# 5. The response will confirm the successful addition of the measurement.
@goal_bp.route('/add_measurementg', methods=['POST'])
def add_measurementg_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys
    
    # Ensure 'goal_name' is provided in the request
    goal_name1 = data.get('goal_name')
    if not goal_name1:
        return jsonify({"error": "Missing required field: goal_name"}), 400

    # Find the goal by 'goal_name'
    goal = goals_collection.find_one({"basic_info.goal_name": goal_name1})
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    measurement_data = data.get('measurement', {})
    # Ensure measurement data is provided
    if not measurement_data:
        return jsonify({"error": "No measurement data provided"}), 400

    # Prepare the new measurement in the required format
    new_measurement = {
        "measurement_name": measurement_data.get("measurement_name"),
        "unit_of_measure": measurement_data.get("unit_of_measure"),
        "start_date": measurement_data.get("start_date"),
        "end_date": measurement_data.get("end_date"),
        "comments": measurement_data.get("comments"),
        "target_type": measurement_data.get("target_type"),
        "target_value": measurement_data.get("target_value"),
        "actual_value": measurement_data.get("actual_value")
    }


    # Perform the update to add the new measurement to the 'measurements' array and update the 'updated_at' timestamp
    result = goals_collection.update_one(
        {"basic_info.goal_name": goal_name1}, 
        {
            "$push": {"measurements": new_measurement},
            "$set": {"updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        }
    )

    return jsonify({
        "message": "Measurement added successfully"
    }), 200

# HR or Manager Route to Add a Task to a Goal
# This route allows HR or managers to add a new task to a specific goal in the `goals_collection`.
# 1. The `goal_name` is required to identify the goal to which the task will be added.
# 2. Task data must be provided, including fields like `name`, `type`, `status`, `priority`, `start_date`, `target_completion_date`, etc.
# 3. The new task will be added to the `tasks` array for the goal.
# 4. The `updated_at` field will be automatically set to the current date and time after the task is added.
# 5. The response will confirm the successful addition of the task.
@goal_bp.route('/add_taskg', methods=['POST'])
def add_taskg_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Ensure 'goal_name' is provided in the request
    goal_name1 = data.get('goal_name')
    if not goal_name1:
        return jsonify({"error": "Missing required field: goal_name"}), 400

    # Find the goal by 'goal_name'
    goal = goals_collection.find_one({"basic_info.goal_name": goal_name1})
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    task_data = data.get('task', {})
    # Ensure task data is provided
    if not task_data:
        return jsonify({"error": "No task data provided"}), 400

    # Prepare the new task in the required format
    new_task = {
        "name": task_data.get("name"),
        "type": task_data.get("type"),
        "status": task_data.get("status"),
        "priority": task_data.get("priority"),
        "comments": task_data.get("comments", []),  # Ensure comments is a list
        "completion_percentage": task_data.get("completion_percentage"),
        "start_date": task_data.get("start_date"),
        "target_completion_date": task_data.get("target_completion_date"),
        "related_link": task_data.get("related_link", [])  # Ensure related_link is a list
    }


    # Perform the update to add the new measurement to the 'measurements' array and update the 'updated_at' timestamp
    result = goals_collection.update_one(
        {"basic_info.goal_name": goal_name1}, 
        {
            "$push": {"tasks": new_task},
            "$set": {"updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        }
    )

    return jsonify({
        "message": "new_task added successfully"
    }), 200

# HR or Manager Route to Update the Start Date and Target Completion Date for Goals
# This route allows HR or managers to filter and update the start date and target completion date for goals in the `my_goals_collection`.
# 1. Filter criteria must be provided in the request to identify the goals to be updated. 
#    - The filter can include fields like `person_name`, `goal_plan_assigned`, `goal_name`, etc.
# 2. The fields to be updated, such as the start date or target completion date, must also be provided.
# 3. The route ensures that critical fields like `person_name`, `goal_name`, and other mandatory fields are not updated.
# 4. For each matched goal, the `updated_at` timestamp is automatically set to the current date and time.
# 5. The update operation is applied to all matching goals, and the response includes the number of goals matched and updated.
@goal_bp.route('/date_and_goal_type', methods=['POST'])
def filter_and_update_my_goals():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Separate filter criteria from update data
    filter_criteria = data.get('filter', {})
    update_fields = data.get('update', {})

    # Ensure at least one filter criterion is provided
    if not filter_criteria:
        return jsonify({"error": "No filter criteria provided"}), 400

    # Ensure at least one field to update is provided
    if not update_fields:
        return jsonify({"error": "No fields to update provided"}), 400

    # Prepare the filter query for MongoDB
    query = {}
    for key, value in filter_criteria.items():
        formatted_key = key.lower().replace(' ', '_')
        query[formatted_key] = value

    # Find matching documents
    matched_goals = list(my_goals_collection.find(query))
    if not matched_goals:
        return jsonify({"error": "No matching goals found"}), 404

    # Define mandatory fields that should not be updated
    mandatory_fields = {
        "person_name", 
        "goal_plan_assigned", 
        "review_period", 
        "performance_document_type", 
        "goal_name", 
        "progress",
        "measurements",
        "tasks",
        "feedback"
    }

    # Prepare update data only for fields present in the 'update' part of the request
    update_data = {}

    # Iterate over each field in 'update_fields' and add to 'update_data' if it's not a mandatory field
    for key, value in update_fields.items():
        formatted_key = key.lower().replace(' ', '_')
        if formatted_key not in mandatory_fields:
            update_data[formatted_key] = value

    # Always update the 'updated_at' timestamp
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Perform the update on all matched documents
    if update_data:
        result = my_goals_collection.update_many(query, {"$set": update_data})
        return jsonify({
            "message": "Goals updated successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }), 200

    return jsonify({"error": "No valid updates were made"}), 400

# Employee Route to Update the Progress of a Goal
# This route allows an employee to update the progress of a specific goal in the `my_goals_collection`.
# 1. Required fields include `person_name`, `goal_name`, `start_date`, `target_completion_date`, and `progress`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks whether the goal exists for the employee based on the provided `person_name`, `goal_name`, `start_date`, and `target_completion_date`.
#    - If the goal is not found, an error is returned.
# 3. If the goal exists, the `progress` field is updated, and the `updated_at` timestamp is set to the current date and time.
# 4. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/update_progress', methods=['POST'])
def update_goal_progress():
    data = lowercase_keys(request.json)

    # Define required fields
    required_fields = ["person_name", "goal_name", "start_date", "target_completion_date", "progress"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if the worker exists with the given criteria
    worker_exists = my_goals_collection.find_one({
        'person_name': data.get("person_name"),
        'goal_name': data.get("goal_name"),
        'start_date': data.get("start_date"),
        'target_completion_date': data.get("target_completion_date")
    })
    
    if not worker_exists:
        return jsonify({"error": "person with given details not found"}), 404

    # Prepare the update data
    update_data = {
        'progress': data.get('progress'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Perform the update on the matched document
    result = my_goals_collection.update_one({
        'person_name': data.get("person_name"),
        'goal_name': data.get("goal_name"),
        'start_date': data.get("start_date"),
        'target_completion_date': data.get("target_completion_date")
    }, {"$set": update_data})
    send_email_on_goal_progress_updated(result)
    return jsonify({
        "message": "Progress updated successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }), 200

# HR or Manager Route to Add a Measurement to a Goal
# This route allows HR or managers to add a new measurement to one or more goals in the `my_goals_collection`.
# 1. Filter criteria must be provided to identify the goals where the measurement will be added.
#    - The filter can include fields like `person_name`, `goal_name`, `goal_plan_assigned`, etc.
# 2. Measurement data must be provided, including fields like `measurement_name`, `unit_of_measure`, `start_date`, `end_date`, etc.
# 3. The new measurement will be added to the `measurements` array for the matching goals.
# 4. The `updated_at` field will be automatically set to the current date and time for all updated goals.
# 5. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/add_measurement', methods=['POST'])
def add_measurement_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Separate filter criteria from measurement data
    filter_criteria = data.get('filter', {})
    measurement_data = data.get('measurement', {})

    # Ensure at least one filter criterion is provided
    if not filter_criteria:
        return jsonify({"error": "No filter criteria provided"}), 400

    # Ensure measurement data is provided
    if not measurement_data:
        return jsonify({"error": "No measurement data provided"}), 400

    # Prepare the filter query for MongoDB
    query = {}
    for key, value in filter_criteria.items():
        formatted_key = key.lower().replace(' ', '_')
        query[formatted_key] = value

    # Check if the goal exists
    matched_goals = list(my_goals_collection.find(query))
    if not matched_goals:
        return jsonify({"error": "No matching goals found"}), 404

    # Prepare the new measurement in the required format
    new_measurement = {
        "measurement_name": measurement_data.get("measurement_name"),
        "unit_of_measure": measurement_data.get("unit_of_measure"),
        "start_date": measurement_data.get("start_date"),
        "end_date": measurement_data.get("end_date"),
        "comments": measurement_data.get("comments"),
        "target_type": measurement_data.get("target_type"),
        "target_value": measurement_data.get("target_value"),
        "actual_value": measurement_data.get("actual_value")
    }

    # Perform the update to add the new measurement to the 'measurements' array
    update_data = {
        "$push": {"measurements": new_measurement},
        "$set": {"updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    }

    result = my_goals_collection.update_many(query, update_data)
    
    return jsonify({
        "message": "Measurement added successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }), 200

# HR or Manager Route to Add a Task to a Goal
# This route allows HR or managers to add a new task to one or more goals in the `my_goals_collection`.
# 1. Filter criteria must be provided to identify the goals where the task will be added.
#    - The filter can include fields like `person_name`, `goal_name`, `goal_plan_assigned`, etc.
# 2. Task data must be provided, including fields like `name`, `type`, `status`, `priority`, etc.
# 3. The new task will be added to the `tasks` array for the matching goals.
# 4. The `updated_at` field will be automatically set to the current date and time for all updated goals.
# 5. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/add_task', methods=['POST'])
def add_task_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Separate filter criteria from task data
    filter_criteria = data.get('filter', {})
    task_data = data.get('task', {})

    # Ensure at least one filter criterion is provided
    if not filter_criteria:
        return jsonify({"error": "No filter criteria provided"}), 400

    # Ensure task data is provided
    if not task_data:
        return jsonify({"error": "No task data provided"}), 400

    # Prepare the filter query for MongoDB
    query = {}
    for key, value in filter_criteria.items():
        formatted_key = key.lower().replace(' ', '_')
        query[formatted_key] = value

    # Check if the goal exists
    matched_goals = list(my_goals_collection.find(query))
    if not matched_goals:
        return jsonify({"error": "No matching goals found"}), 404

    # Prepare the new task in the required format
    new_task = {
        "name": task_data.get("name"),
        "type": task_data.get("type"),
        "status": task_data.get("status"),
        "priority": task_data.get("priority"),
        "comments": task_data.get("comments", []),  # Ensure comments is a list
        "completion_percentage": task_data.get("completion_percentage"),
        "start_date": task_data.get("start_date"),
        "target_completion_date": task_data.get("target_completion_date"),
        "related_link": task_data.get("related_link", [])  # Ensure related_link is a list
    }

    # Perform the update to add the new task to the 'tasks' array
    update_data = {
        "$push": {"tasks": new_task},
        "$set": {"updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    }

    result = my_goals_collection.update_many(query, update_data)
    
    return jsonify({
        "message": "Task added successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }), 200

# Employee Route to Update the Status of a Task in a Goal
# This route allows an employee to update the status of a specific task in a goal within the `my_goals_collection`.
# 1. Required fields include `person_name`, `goal_name`, `start_date`, `target_completion_date`, `task_name`, and `status`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the goal exists for the employee based on the provided `person_name`, `goal_name`, `start_date`, and `target_completion_date`.
#    - If the goal or the task is not found, an error is returned.
# 3. If the goal and task are found, the status of the task is updated, and the `updated_at` timestamp is automatically set to the current date and time.
# 4. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/update_task_status', methods=['POST'])
def update_task_status():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Define required fields
    required_fields = ["person_name", "goal_name", "start_date", "target_completion_date", "task_name", "status"]
    missing_fields = [field for field in required_fields if field not in data]
    
    # Check if any required fields are missing
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if the goal exists with the given criteria
    goal_document = my_goals_collection.find_one({
        'person_name': data.get("person_name"),
        'goal_name': data.get("goal_name"),
        'start_date': data.get("start_date"),
        'target_completion_date': data.get("target_completion_date")
    })
    
    if not goal_document:
        return jsonify({"error": "No matching goals found"}), 404

    # Ensure the task to update is identified uniquely by task name
    task_name_to_update = data.get('task_name')
    if not task_name_to_update:
        return jsonify({"error": "Task name to update is required"}), 400

    # Check if the specified task name exists in the 'tasks' array
    task_exists = False
    if 'tasks' in goal_document:
        for task in goal_document['tasks']:
            if task.get('name') == task_name_to_update:
                task_exists = True
                break
    
    if not task_exists:
        return jsonify({"error": f"Task '{task_name_to_update}' not found in the specified goal"}), 404

    # Prepare the update query for the specific task status
    update_query = {
        "$set": {
            "tasks.$[elem].status": data.get('status'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    # Array filter to match the specific task within the tasks array
    array_filters = [{"elem.name": task_name_to_update}]

    # Debugging output: print the array filters and update query
    print(f"Array Filters: {array_filters}")
    print(f"Update Query: {update_query}")

    try:
        # Perform the update and return the updated document
        result = my_goals_collection.update_one(
            {
                'person_name': data.get("person_name"),
                'goal_name': data.get("goal_name"),
                'start_date': data.get("start_date"),
                'target_completion_date': data.get("target_completion_date")
            },
            update_query,
            array_filters=array_filters
        )

        if result.modified_count == 0:
            print("Update did not modify any documents.")
            return jsonify({"error": "Task status was not updated"}), 400

        # Debugging output: print the result of the update operation
        print(f"Update Result: Matched Count = {result.matched_count}, Modified Count = {result.modified_count}")
        
        send_email_on_goal_task_progress_update(result)
        return jsonify({
            "message": "Task status updated successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }), 200

    except Exception as e:
        print(f"Exception during update: {e}")
        return jsonify({"error": f"Update failed: {e}"}), 500

# Employee Route to Update Task Completion Percentage
# This route allows an employee to update the completion percentage of a specific task in a goal within the `my_goals_collection`.
# 1. Required fields include `person_name`, `goal_name`, `start_date`, `target_completion_date`, `task_name`, and `completion_percentage`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the goal exists for the employee based on the provided `person_name`, `goal_name`, `start_date`, and `target_completion_date`.
#    - If the goal or the task is not found, an error is returned.
# 3. If the goal and task are found, the `completion_percentage` of the task is updated, and the `updated_at` timestamp is automatically set to the current date and time.
# 4. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/update_task_completion', methods=['POST'])
def update_task_completion():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Define required fields
    required_fields = ["person_name", "goal_name", "start_date", "target_completion_date", "task_name", "completion_percentage"]
    missing_fields = [field for field in required_fields if field not in data]
    
    # Check if any required fields are missing
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if the goal exists with the given criteria
    goal_document = my_goals_collection.find_one({
        'person_name': data.get("person_name"),
        'goal_name': data.get("goal_name"),
        'start_date': data.get("start_date"),
        'target_completion_date': data.get("target_completion_date")
    })
    
    if not goal_document:
        return jsonify({"error": "No matching goals found"}), 404

    # Ensure the task to update is identified uniquely by task name
    task_name_to_update = data.get('task_name')
    if not task_name_to_update:
        return jsonify({"error": "Task name to update is required"}), 400

    # Check if the specified task name exists in the 'tasks' array
    task_exists = False
    if 'tasks' in goal_document:
        for task in goal_document['tasks']:
            if task.get('name') == task_name_to_update:
                task_exists = True
                break
    
    if not task_exists:
        return jsonify({"error": f"Task '{task_name_to_update}' not found in the specified goal"}), 404

    # Prepare the update query for the specific task completion percentage
    update_query = {
        "$set": {
            "tasks.$[elem].completion_percentage": data.get('completion_percentage'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    # Array filter to match the specific task within the tasks array
    array_filters = [{"elem.name": task_name_to_update}]

    # Debugging output: print the array filters and update query
    print(f"Array Filters: {array_filters}")
    print(f"Update Query: {update_query}")

    try:
        # Perform the update and return the updated document
        result = my_goals_collection.update_one(
            {
                'person_name': data.get("person_name"),
                'goal_name': data.get("goal_name"),
                'start_date': data.get("start_date"),
                'target_completion_date': data.get("target_completion_date")
            },
            update_query,
            array_filters=array_filters
        )

        if result.modified_count == 0:
            print("Update did not modify any documents.")
            return jsonify({"error": "Task completion percentage was not updated"}), 400

        # Debugging output: print the result of the update operation
        print(f"Update Result: Matched Count = {result.matched_count}, Modified Count = {result.modified_count}")
        send_email_on_goal_task_completion_update(result)
        return jsonify({
            "message": "Task completion percentage updated successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }), 200

    except Exception as e:
        print(f"Exception during update: {e}")
        return jsonify({"error": f"Update failed: {e}"}), 500

# Manager Route to Add Feedback to an Employee's Goal(as per ankit k)
# This route allows a manager to add feedback to an employee's goal within the `my_goals_collection`.
# 1. Required fields include `person_name`, `goal_name`, `start_date`, `target_completion_date`, and `feedback`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the goal exists for the employee based on the provided `person_name`, `goal_name`, `start_date`, and `target_completion_date`.
#    - If the goal is not found, an error is returned.
# 3. Feedback data must be provided, which includes `comment`, `rating`, and `given_by` (default: "Manager").
#    - The feedback is appended to the `feedback` array in the goal.
# 4. The `updated_at` field is automatically set to the current date and time after feedback is added.
# 5. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/add_feedback', methods=['POST'])
def add_feedback_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Define required fields for identifying the document and feedback data
    required_fields = ["person_name", "goal_name", "start_date", "target_completion_date", "feedback"]
    missing_fields = [field for field in required_fields if field not in data]

    # Check if any required fields are missing
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if the goal exists with the given criteria
    goal_document = my_goals_collection.find_one({
        'person_name': data.get("person_name"),
        'goal_name': data.get("goal_name"),
        'start_date': data.get("start_date"),
        'target_completion_date': data.get("target_completion_date")
    })
    
    if not goal_document:
        return jsonify({"error": "No matching goals found"}), 404

    # Extract feedback data
    feedback_data = data.get('feedback')
    if not feedback_data:
        return jsonify({"error": "Feedback data is required"}), 400
    
    fdata= {
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "comment":feedback_data.get('comment'),
        "rating": feedback_data.get('rating','N/A'),
        "given_by": feedback_data.get('given_by','Manager')
    }
    # Prepare the update query to add feedback
    update_query = {
        "$push": {
            "feedback": fdata
        },
        "$set": {
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": feedback_data.get('given_by','Manager')
        }
    }

    try:
        # Perform the update to add feedback to the feedback array
        result = my_goals_collection.update_one(
            {
                'person_name': data.get("person_name"),
                'goal_name': data.get("goal_name"),
                'start_date': data.get("start_date"),
                'target_completion_date': data.get("target_completion_date")
            },
            update_query
        )

        if result.modified_count == 0:
            print("Feedback was not added to any documents.")
            return jsonify({"error": "Feedback was not added"}), 400

        # Debugging output: print the result of the update operation
        print(f"Update Result: Matched Count = {result.matched_count}, Modified Count = {result.modified_count}")
        send_email_on_feedback_of_goal(result)
        return jsonify({
            "message": "Feedback added successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }), 200

    except Exception as e:
        print(f"Exception during update: {e}")
        return jsonify({"error": f"Update failed: {e}"}), 500

# Manager or HR Route to Add a Comment to a Goal
# This route allows a manager or HR to add a comment to one or more goals in the `my_goals_collection`.
# 1. Filter criteria must be provided to identify the goals where the comment will be added.
#    - The filter can include fields like `person_name`, `goal_name`, `goal_plan_assigned`, etc.
# 2. Comment data must be provided, which includes the content of the comment.
# 3. The new comment will be added to the `comments` array for the matching goals.
# 4. The `updated_at` field will be automatically set to the current date and time for all updated goals.
# 5. The response includes the number of goals matched and updated, along with a success message.
@goal_bp.route('/add_comment', methods=['POST'])
def add_comment_to_goal():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Separate filter criteria from comment data
    filter_criteria = data.get('filter', {})
    comment_data = data.get('comment')

    # Ensure at least one filter criterion is provided
    if not filter_criteria:
        return jsonify({"error": "No filter criteria provided"}), 400

    # Ensure comment data is provided
    if not comment_data:
        return jsonify({"error": "No comment data provided"}), 400

    # Prepare the filter query for MongoDB
    query = {}
    for key, value in filter_criteria.items():
        formatted_key = key.lower().replace(' ', '_')
        query[formatted_key] = value

    # Check if the goal exists
    matched_goals = list(my_goals_collection.find(query))
    if not matched_goals:
        return jsonify({"error": "No matching goals found"}), 404


    # Perform the update to add the new comment to the 'comments' array
    update_data = {
        "$push": {"comments": comment_data},
        "$set": {"updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    }

    result = my_goals_collection.update_many(query, update_data)
    
    return jsonify({
        "message": "Comment added successfully",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }), 200

# HR or Manager Route to Filter Goals Based on Specific Criteria
# This route allows HR or managers to filter goals from the `my_goals_collection` based on provided criteria.
# 1. Filter criteria must be provided in the request. 
#    - The criteria can include fields like `person_name`, `goal_name`, `goal_plan_assigned`, etc.
# 2. The route constructs a filter query based on the provided criteria and queries the `my_goals_collection`.
#    - The keys in the filter criteria are formatted to match the database fields (lowercase and underscores).
# 3. If matching goals are found, the route returns the goals in the response. 
#    - The `_id` field is excluded from the returned results for simplicity.
# 4. If no goals match the criteria, an error is returned indicating that no matching goals were found.
# 5. The response includes a message and the list of matching goals, along with a status of 200 (OK) if successful.
@goal_bp.route('/filter_goals', methods=['POST'])
def filter_goals():
    data = lowercase_keys(request.json)  # Ensure data is consistent with lowercase keys

    # Get filter criteria from the request
    filter_criteria = data.get('filter', {})

    # Ensure at least one filter criterion is provided
    if not filter_criteria:
        return jsonify({"error": "No filter criteria provided"}), 400

    # Prepare the filter query for MongoDB
    query = {}
    for key, value in filter_criteria.items():
        formatted_key = key.lower().replace(' ', '_')
        query[formatted_key] = value

    # Find matching documents
    matched_goals = list(my_goals_collection.find(query, {"_id": 0}))
    if not matched_goals:
        return jsonify({"error": "No matching goals found"}), 404

    # Return the matching goals
    return jsonify({
        "message": "Matching goals found",
        "matched_goals": matched_goals
    }), 200
