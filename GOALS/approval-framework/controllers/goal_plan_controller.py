from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config
 
goal_plan_bp = Blueprint('goal_plan_bp', __name__)
 
# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
eligibility_profile_collection = db[config.ELIGIBILITY_PROFILES_COLLECTION_NAME]
employee_collection = db['s_employeedetails_2']  # Updated to the correct collection
include_exclude_collection = db[config.INCLUDE_EXCLUDE_COLLECTION_NAME]
 
# Helper function to convert keys to lowercase
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower(): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data
 
# Modified get_matching_employees function
def get_matching_employees(eligibility_profiles):
    matched_employees = set()
    for profile in eligibility_profiles:
        criteria = profile["create_participant_profile"]["eligibility_criteria"]
        query = {}
 
        # Construct query based on non-null criteria fields in personal section
        personal_criteria = criteria.get("personal", {})
        for key, value in personal_criteria.items():
            if value and value.lower() not in ["n/a", "all","N/A","All"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value
 
        # Construct query based on non-null criteria fields in employment section
        employment_criteria = criteria.get("employment", {})
        for key, value in employment_criteria.items():
            if value and value.lower() not in ["n/a", "all","N/A","All"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value
                print("value:",value,"\n")
 
        employees = employee_collection.find(query)
        for employee in employees:
            matched_employees.add(employee["person_number"])
 
    return list(matched_employees)
 
# Function to validate employee IDs
def validate_employee_ids(employee_ids):
    # Retrieve all valid employee IDs from the collection
    valid_employees = set(str(employee["person_number"]) for employee in employee_collection.find({}, {"person_number": 1}))
    print(f"Valid Employees: {valid_employees}")
    valid_ids = [str(emp_id) for emp_id in employee_ids if str(emp_id) in valid_employees]
    print(f"Validated Employee IDs: {valid_ids}")
    return valid_ids
 
@goal_plan_bp.route('/', methods=['POST'])
def create_goal_plan():
    data = lowercase_keys(request.json)
 
    # Extract the details from the input
    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    goal_plan_name = goal_plan_details.get("goal_plan_name", "")
    goal_plan_name =goal_plan_details["goal plan name"]
    #print('goal_plan_details',goal_plan_details)
 
    # Retrieve corresponding eligibility profiles from the eligibility profile collection by name
    eligibility_profiles = []
    
    # MODIFICATION: Change matched_employees to a dictionary
    matched_employees = {}  # Change to dictionary to map profile names to matched employees

    for profile_name in eligibility_profile_names:
        profile_data = eligibility_profile_collection.find_one({"create_participant_profile.eligibility_profile_definition.name": profile_name})
        if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligibility_profiles.append(profile_data)
 
            # MODIFICATION: Get matching employees for each profile and store in dictionary
            matched_employees[profile_name] = get_matching_employees([profile_data])

            print("*" * 15)
            print('profile_name : ', profile_name)
            print('matched_employees', matched_employees[profile_name])
            print("*" * 15)
 
    # Retrieve include/exclude information based on goal plan name
    print('goal_plan_name : ', goal_plan_name)
    include_exclude = include_exclude_collection.find_one({'goal_plan_name': goal_plan_name})

    print("*" * 15)

    print('include exclude : ',include_exclude)

    print("*" * 15)
    include_ids = set()
    exclude_ids = set()
 
    if include_exclude:
        include_ids = set(validate_employee_ids(include_exclude.get("include", [])))
        exclude_ids = set(validate_employee_ids(include_exclude.get("exclude", [])))
        print("*" * 15)
        print('include : ',include_ids)
        print('exclude : ',exclude_ids)

        print("*" * 15)
 
        # # MODIFICATION: Add included employees to each profile's matched employees
        # for profile_name in matched_employees:
        #     matched_employees[profile_name].update(include_ids)
 
        # # MODIFICATION: Remove excluded employees from each profile's matched employees
        # for profile_name in matched_employees:
        #     matched_employees[profile_name].difference_update(exclude_ids)
 
    # Debugging output to ensure include and exclude IDs are being processed
    print(f"Include IDs: {include_ids}")
    print(f"Exclude IDs: {exclude_ids}")
    print("*" * 15)
    print('include : ',include_ids)
    print('exclude : ',exclude_ids)

    print("*" * 15)

 
    # MODIFICATION: Create the goal plan document without include/exclude fields
    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,  # Directly insert the provided goals
        "eligibility_profiles": [
            {
                "name": ep["create_participant_profile"]["eligibility_profile_definition"]["name"],
                "employee_id": list(matched_employees[ep["create_participant_profile"]["eligibility_profile_definition"]["name"]])
            }
            for ep in eligibility_profiles
        ],
        "include":list(include_ids),
        'exclude' : list(exclude_ids)


    }
 
    print("Goal Plan Document: ", goal_plan_document)
 
    # Insert the goal plan into MongoDB
    goal_plan_id = goal_plan_collection.insert_one(goal_plan_document).inserted_id
    new_goal_plan = goal_plan_collection.find_one({'_id': goal_plan_id})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])
 
    # Return the newly created goal plan
    return jsonify(new_goal_plan), 201

 
@goal_plan_bp.route('/', methods=['GET'])
def get_goal_plans():
    # Retrieve all goal plans from the database
    goal_plans = list(goal_plan_collection.find())
    for goal_plan in goal_plans:
        goal_plan['_id'] = str(goal_plan['_id'])
    return jsonify(goal_plans), 200
 
@goal_plan_bp.route('/<goal_plan_id>', methods=['GET'])
def get_goal_plan(goal_plan_id):
    # Retrieve a specific goal plan by ID
    goal_plan = goal_plan_collection.find_one({'_id': ObjectId(goal_plan_id)})
    if goal_plan:
        goal_plan['_id'] = str(goal_plan['_id'])
        return jsonify(goal_plan), 200
    else:
        return jsonify({'error': 'Goal plan not found'}), 404
 
@goal_plan_bp.route('/<goal_plan_id>', methods=['PUT'])
def update_goal_plan(goal_plan_id):
    data = lowercase_keys(request.json)
    result = goal_plan_collection.update_one({'_id': ObjectId(goal_plan_id)}, {'$set': data})
    if result.matched_count:
        updated_goal_plan = goal_plan_collection.find_one({'_id': ObjectId(goal_plan_id)})
        updated_goal_plan['_id'] = str(updated_goal_plan['_id'])
        return jsonify(updated_goal_plan), 200
    else:
        return jsonify({'error': 'Goal plan not found'}), 404
 
@goal_plan_bp.route('/<goal_plan_id>', methods=['DELETE'])
def delete_goal_plan(goal_plan_id):
    result = goal_plan_collection.delete_one({'_id': ObjectId(goal_plan_id)})
    if result.deleted_count:
        return jsonify({'message': 'Goal plan deleted successfully'}), 200
    else:
        return jsonify({'error': 'Goal plan not found'}), 404