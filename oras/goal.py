from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from jsonschema import validate, ValidationError
# from algorithms.general_algo import get_database

goal_bp = Blueprint('add_goal_bp', __name__)

MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"


client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
my_goals_collection = db['PGM_my_goals']
goals_collection = db["PGM_goal"]
employee_collection = db['HRM_employee_details']
derived_employee_collection = db['HRM_employee_derived_details']
eligibility_profiles_collection = db["PGM_eligibility_profiles"]
goal_plan_collection = db["PGM_goal_plan"]
my_goals_plan_collection = db["PGM_my_goal_plan_goals"]
goal_offering_collection= db["PGM_goal_offering"]
mass_assign_goal_based_on_goal_plan= db["PGM_assign_oras_goals"]


# Helper function to get matching employees based on eligibility name
def get_matching_employees(eligibility_name):
    eligibility_profile = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": eligibility_name})
    # print(f"Eligibility Profile: {eligibility_profile}")
    
    if not eligibility_profile:
        return []

    eligibility_criteria = eligibility_profile.get("eligibility_criteria", {})

    # Function to check if a field exists in the collection
    def field_exists(collection, field_name):
        return collection.find_one({field_name: {"$exists": True}}) is not None

    def construct_query(criteria, collection):
        query = {}
        for key, value in criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_')
                if field_exists(collection, field_name):
                   query[field_name] = {"$regex": f"^{value}$", "$options": "i"}
        return query

    # Collect all personal and employment criteria fields
    personal_criteria = eligibility_criteria.get("personal", {})
    employment_criteria = eligibility_criteria.get("employment", {})
    all_criteria = {**personal_criteria, **employment_criteria}

    # Construct queries separately for each collection
    query_for_employee_details = construct_query(all_criteria, employee_collection)
    query_for_derived_employee_details = construct_query(all_criteria, derived_employee_collection)

    employees = list(employee_collection.find(query_for_employee_details))

    derived_employees = list(derived_employee_collection.find(query_for_derived_employee_details))

    # Intersect the two sets of employees to get the common ones
    employee_names_from_hrm = {employee.get('person_name') for employee in employees}
    employee_names_from_derived = {employee.get('person_name') for employee in derived_employees}
    common_employee_names = employee_names_from_hrm.intersection(employee_names_from_derived)
    
    return list(common_employee_names)


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
        },
        "library_info": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "type": {"type": "string"},
                "available_to": {"type": "string"},
                "legal_employer": {"type": "string"},
                "business_unit": {"type": "string"},
                "department": {"type": "string"},
                "external_id": {"type": "string"}
            },
            "required": ["status", "type", "available_to", "legal_employer", "business_unit", "department", "external_id"]
        },
        "eligibility_name": { 
                "type": "string"
        }
    },
    "required": ["basic_info", "measurements", "tasks", "library_info", "eligibility_name"]
}


# create a goal
@goal_bp.route('/create', methods=['POST'])
def create_goal():
    data = request.json

    # Validate input JSON against the schema
    try:
        validate(instance=data, schema=goal_schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid input data", "message": str(e)}), 400

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")


    eligibility_name = data.get("eligibility_name", "")
    
    eligibility_name1 = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": eligibility_name})
    if not eligibility_name1:
        return jsonify({"error": "eligibility not found in eligibility collection"}), 404 
    
    employees = get_matching_employees(eligibility_name)

    data["employees"] = employees
    data["updated_by"]= updated_by
    data["updated_at"]= current_time

    goal_id = goals_collection.insert_one(data).inserted_id
    new_goal = goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    print(f"Inserted new goal: {new_goal}")
    return jsonify(new_goal), 201

# assign goal to a particular employee
@goal_bp.route('/assign', methods=['POST'])
def add_goal():
    data = request.json
    required_fields = ["person_name", "goal_name", "goal_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    worker_exists = employee_collection.find_one({'person_name': data.get("person_name")})
    if worker_exists:
      print("exist")
    else:
     return jsonify({"error": "Person name not exist"}), 400

    goal1 = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal1:
        return jsonify({"error": "goal not found in goal collection"}), 404 

     # Check if the goal_plan exists in goal_plan_collection
    if data.get('goal_plan_name'):
     goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name')})
     if not goal_plan1:
        return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404
    
    updated_by = data.get('updated_by', 'Admin')
    goal_type = data.get('goal_type')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("Received data to add goal:", data)
    
    # Prepare the goal data
    goal_data = {
        "person_name": data.get("person_name"),
        "goal_plan_assigned": data.get("goal_plan_name","N/A"),
        "goal_name": data.get("goal_name"),
        "goal_type": goal_type,
        "progress": data.get("progress", "Not started"),
        "measurement": goal1.get("measurements"),
        "comments": data.get("comments", []),
        "feedback": data.get("feedback", []),
        "updated_by": updated_by,
        "updated_at": current_time
    }
    
    print("Prepared goal data:", goal_data)
    
    # Insert the goal into the my_goals collection
    goal_id = my_goals_collection.insert_one(goal_data).inserted_id
    new_goal = my_goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    
    print("Inserted new goal:", new_goal)
    return jsonify(new_goal), 201

# goal offering
@goal_bp.route('/goal_offering', methods=['POST'])
def goal_offering():
    data = request.json
    # Validate necessary fields are present
    if 'person_name' not in data or 'goal_name' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    worker_exists = employee_collection.find_one({'person_name': data.get("person_name")})
    if worker_exists:
      print("exist")
    else:
     return jsonify({"error": "Person name not exist"}), 400
    
    
    goal = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal:
        return jsonify({"error": "goal not found in goal collection"}), 404 

     # Check if the goal_plan exists in goal_plan_collection
    if data.get('goal_plan_name'):
     goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name')})
     if not goal_plan1:
        return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404
    

    print("Received data to add goal:", data)
    
    # Prepare the goal data
    goal_data = {
        "person_name": data.get("person_name"),
        "goal_plan_assigned": data.get("goal_plan_name","N/A"),
        "goal_name": data.get("goal_name"),
        "status": "approval_required",
        "timestamp": current_time
    }
    
    print("Prepared goal data:", goal_data)
    
    # Insert the goal into the my_goals collection
    goal_id = goal_offering_collection.insert_one(goal_data).inserted_id
    new_goal = goal_offering_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    
    print("Inserted new goal:", new_goal)
    return jsonify(new_goal), 201

@goal_bp.route('/process_goal', methods=['POST'])
def process_goal():
    data = request.json
    if 'person_name' not in data or 'goal_name' not in data or 'status' not in data:
     return jsonify({"error": "Person name, goal name, and status are required"}), 400
    
    updated_by = data.get('updated_by', 'Admin')
    goal_type = data.get('goal_type','development')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    person_name = data.get("person_name")
    goal_name = data.get("goal_name")
    status = data.get("status")
    
    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400
    
    # Fetch the goal from the goal offering collection
    goal = goal_offering_collection.find_one({
        "person_name": person_name,
        "goal_name": goal_name
    })
    
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
    
    
    goal1 = goals_collection.find_one({"basic_info.goal_name": goal_name})

    if status == "approved":
        # Move the goal to the my goals collection
        my_goals_collection.insert_one({
            "person_name": goal["person_name"],
            "goal_plan_assigned": goal["goal_plan_assigned"],
            "goal_name": goal["goal_name"],
            "goal_type": goal_type,
            "progress": "Not started",
            "measurement": goal1.get("measurements"),
            "comments": [],
            "feedback": [],
            "updated_by": updated_by,
            "updated_at": current_time
        })
        goal_offering_collection.update_one(
            {
                "person_name": person_name,
                "goal_name": goal_name
            },
            {'$set': {"status": "approved",
                       "timestamp":current_time}}
        )
    else:
        # Update the status of the goal to "rejected" in the goal offering collection
        goal_offering_collection.update_one(
            {
                "person_name": person_name,
                "goal_name": goal_name
            },
            {'$set': {"status": "rejected",
                      "timestamp":current_time}}
        )

    print(f"Processed goal with status {status} for person {person_name} and goal {goal_name}")
    return jsonify({"message": "Goal processed", "person_name": person_name, "goal_name": goal_name, "status": status}), 200

@goal_bp.route('/mass_assign', methods=['POST'])
def assign_goal_to_all_employees():
    data = request.json
    if 'goal_type' not in data or 'eligibility_name' not in data or 'goal_name' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    
    eligibility_name1 = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": data.get('eligibility_name')})
    if not eligibility_name1:
         return jsonify({"error": "eligibility not found in eligibility collection"}), 404 

    goal1 = goals_collection.find_one({"basic_info.goal_name": data.get('goal_name')})
    if not goal1:
        return jsonify({"error": "goal not found in goal collection"}), 404 

     # Check if the goal_plan exists in goal_plan_collection
    if data.get('goal_plan_name'):
     goal_plan1 = goal_plan_collection .find_one({"details.goal_plan_name": data.get('goal_plan_name')})
     if not goal_plan1:
        return jsonify({"error": "goal_plan not found in goal_plan collection"}), 404

    eligibility_name = data.get("eligibility_name", "")
    employees = get_matching_employees(eligibility_name)
    # eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    updated_by = data.get('updated_by', 'Admin')
    goal=data.get('goal_name')
    goal_plan_name=data.get('goal_plan_name','N/A')
    goal_type = data.get('goal_type')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    combined_employees = employees

    print("Combined employees:", combined_employees)

    my_goals_entries = []
    for employee_name in combined_employees:
        my_goals_entry = {
            "person_name": employee_name,
            "goal_plan_assigned": goal_plan_name,
            "goal_name": goal,
            "goal_type": goal_type,
            "progress": data.get('progress','Not started'),  # Default value
            "measurement": goal1.get("measurements"),  # Default value
            "comments": [],
            "feedback": [],
            "updated_by": updated_by,
            "updated_at": current_time
            }
        print("Created my_goals entry:", my_goals_entry)
        my_goals_entries.append(my_goals_entry)

    if my_goals_entries:
        print("Inserting entries into my_goals collection")
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        print("Inserted IDs:", inserted_ids)
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])
        print("Converted entry:", entry)

    print("Final my_goals_entries:", my_goals_entries)
    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200

@goal_bp.route('/assign_on_combined_employee_list', methods=['POST'])
def fetch_goals():
    data = request.json
    if 'goal_plan_name' not in data or 'goal_type' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    goal_plan_name = data.get('goal_plan_name')
    goal_type = data.get('goal_type')
    updated_by = data.get('updated_by', 'Admin')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("goal_plan_name:", goal_plan_name)

    # Fetching the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})

    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404

    # Fetch combined employees list
    combined_employees = set(goal_plan.get('combined_employees', []))
    print("Combined employees:", combined_employees)

    # Retrieve the goal names
    goals = goal_plan.get('goals', [])
    print("Goals:", goals)

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

            # Include measurement details from the goal
            my_goals_entry = {
                "person_name": employee_name,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,
                "goal_type": goal_type,
                "progress": data.get('progress', 'Not started'),  # Default value
                "measurement": goal.get('measurements', []),  # Include the measurement from the goal
                "comments": [],
                "feedback": [],
                "updated_by": updated_by,
                "updated_at": current_time
            }
            print("Created my_goals entry:", my_goals_entry)
            my_goals_entries.append(my_goals_entry)

    # Insert into my_goals collection
    if my_goals_entries:
        print("Inserting entries into my_goals collection")
        result = my_goals_plan_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        print("Inserted IDs:", inserted_ids)
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])
        print("Converted entry:", entry)

    print("Final my_goals_entries:", my_goals_entries)
    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200

# Assign goals based on goal eligibility
@goal_bp.route('/assign_on_goal_eligibility', methods=['POST'])
def assign_goals_based_on_goal_eligibility():
    data = request.json
    if 'goal_plan_name' not in data or 'goal_type' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    goal_plan_name = data.get('goal_plan_name')
    goal_type = data.get('goal_type')
    updated_by = data.get('updated_by', 'Admin')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("Received goal_plan_name:", goal_plan_name)

    # Fetch the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})
    print("Fetched goal plan:", goal_plan)

    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404

    # Retrieve the goal names from the goal plan
    goal_names = goal_plan.get("goals", [])
    print("Goal names in the goal plan:", goal_names)

    # Fetch the goals details from the goals collection
    goals = list(goals_collection.find({"basic_info.goal_name": {"$in": goal_names}}))
    print("Fetched goals details:", goals)

    if not goals:
        return jsonify({'error': 'No goals found for the specified goal plan'}), 404

    # Retrieve the combined employees from the goal plan
    combined_employees = set(goal_plan.get('combined_employees', []))
    print("Combined employees:", combined_employees)

    # Creating my_goals collection entries based on goal eligibility
    my_goals_entries = []
    for goal in goals:
        goal_name = goal["basic_info"]["goal_name"]
        eligible_employees = goal.get("employees", [])
        print(f"Processing goal: {goal_name}, Eligible employees: {eligible_employees}")

        # Filter combined employees based on eligible employees for this goal
        filtered_employees = [emp for emp in combined_employees if emp in eligible_employees]
        print(f"Eligible employees for goal {goal_name}:", filtered_employees)

        for employee_name in filtered_employees:
            my_goals_entry = {
                "person_name": employee_name,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,
                "goal_type": goal_type,
                "progress": "Not started",
                "measurement": goal.get('measurements'), # Default value
                "comments": [],
                "feedback": [],
                "updated_by": updated_by,
                "updated_at": current_time
            }
            print("Created my_goals entry:", my_goals_entry)
            my_goals_entries.append(my_goals_entry)

    # Insert into my_goals collection
    if my_goals_entries:
        print("Inserting entries into my_goals collection")
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        print("Inserted IDs:", inserted_ids)
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])
        print("Converted entry:", entry)

    print("Final my_goals_entries:", my_goals_entries)
    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200

@goal_bp.route('/assign_goals', methods=['POST'])
def assign_goals():
    try:
        # Get inputs from request
        data = request.json
        if 'goal_plan_name' not in data or 'goals' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        goal_plan_name = data.get('goal_plan_name')

        # Fetch goal plan details
        goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})
        if not goal_plan:
            return jsonify({"error": "Goal plan not found"}), 404
        
        # Fetch goals by name to be assigned
        goal_names = data.get("goals", [])
        assigned_goals = []
        eligibility_profiles = set()  # Store unique eligibility profiles for fetching employees

        for goal_name in goal_names:
            goal = goals_collection.find_one({"basic_info.goal_name": goal_name})
            if goal:
                assigned_goals.append(goal)
                # Fetch eligibility name associated with the goal
                eligibility_name = goal.get("eligibility_name")
                if eligibility_name:
                    eligibility_profiles.add(eligibility_name)

        if not assigned_goals:
            return jsonify({"error": "No valid goals found"}), 404

        if not eligibility_profiles:
            return jsonify({"error": "No eligibility profiles found for the provided goals"}), 404

        filtered_employees = set()

        # Fetch matching employees for each eligibility profile
        for eligibility_profile_name in eligibility_profiles:
            employees_goal = get_matching_employees(eligibility_profile_name)
            # Intersect with combined employees from goal plan
            combined_employees = set(goal_plan.get("combined_employees", []))
            eligible_employees = set(employees_goal).intersection(combined_employees)
            filtered_employees.update(eligible_employees)

        if not filtered_employees:
            return jsonify({"message": "No employees matched the criteria"}), 404

        # Prepare the assignment data for the mass assign goals collection
        assignment_data = {
            "goal_plan_name": goal_plan_name,
            "eligibility_profiles": list(eligibility_profiles),  # Convert set to list
            "goals": [goal['basic_info']['goal_name'] for goal in assigned_goals],
            "employees": list(filtered_employees),  # Convert set to list for JSON serialization
            "updated_by": data.get('updated_by', 'Admin'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        mass_assign_goal_based_on_goal_plan.insert_one(assignment_data)

        # Prepare entries for my_goals collection
        my_goals_entries = []
        for employee_name in filtered_employees:
            for goal in assigned_goals:
                my_goals_entry = {
                    "person_name": employee_name,
                    "goal_plan_assigned": goal_plan_name,
                    "goal_name": goal['basic_info']['goal_name'],
                    "goal_type": data.get('goal_type', 'development'),
                    "progress": data.get('progress', 'Not started'),  # Default value
                    "measurement": goal.get('measurements', []),  # Include the measurement from the goal
                    "comments": [],
                    "feedback": [],
                    "updated_by": data.get('updated_by', 'Admin'),
                    "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                my_goals_entries.append(my_goals_entry)

        # Insert entries into my_goals collection
        if my_goals_entries:
            result = my_goals_collection.insert_many(my_goals_entries)
            inserted_ids = result.inserted_ids

            # Retrieve the newly inserted documents to include in the response
            my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

        # Convert ObjectIds to strings for JSON serialization
        for entry in my_goals_entries:
            entry['_id'] = str(entry['_id'])

        return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
