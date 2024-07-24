

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

goal_plan_bp = Blueprint('goal_plan_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
eligibility_profile_collection = db[config.ELIGIBILITY_PROFILES_COLLECTION_NAME]
employee_collection = db['s_employeedetails_2']

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
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

        personal_criteria = criteria.get("personal", {})
        for key, value in personal_criteria.items():
            if value and value.lower() not in ["n/a", "all", "N/A", "All"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        employment_criteria = criteria.get("employment", {})
        for key, value in employment_criteria.items():
            if value and value.lower() not in ["n/a", "all", "N/A", "All"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        employees = employee_collection.find(query)
        for employee in employees:
            full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
            matched_employees.add(full_name)

    return list(matched_employees)

# Function to validate employee full names
def validate_employee_full_names(employee_names):
    valid_employees = set(
        f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        for employee in employee_collection.find({}, {"first_name": 1, "last_name": 1})
    )
    valid_full_names = [name for name in employee_names if name in valid_employees]
    return valid_full_names

@goal_plan_bp.route('/', methods=['POST'])
def create_goal_plan():
    data = lowercase_keys(request.json)
    print(f"Received data for goal plan creation: {data}")

    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = data.get("included_workers", [])
    excluded_workers = data.get("excluded_workers", [])

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = goal_plan_details.get("updated_by", "Unknown")
    goal_plan_details["updated_date"] = current_time
    goal_plan_details["updated_by"] = updated_by

    eligibility_profiles = []
    matched_employees = {}

    for profile_name in eligibility_profile_names:
        print(f"Fetching eligibility profile: {profile_name}")
        profile_data = eligibility_profile_collection.find_one({"create_participant_profile.eligibility_profile_definition.name": profile_name})
        if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligibility_profiles.append(profile_data)
            matched_employees[profile_name] = get_matching_employees([profile_data])
        else:
            print(f"Profile not found: {profile_name}")

    # Combine matched employees with included workers, ensuring no duplicates
    combined_workers = set(included_workers)
    for profile_name in matched_employees:
        combined_workers.update(matched_employees[profile_name])
    combined_workers.difference_update(excluded_workers)

    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,
        "eligibility_profiles": [
            {
                "name": ep["create_participant_profile"]["eligibility_profile_definition"]["name"],
                "employees_name": list(combined_workers)  # Include combined workers
            }
            for ep in eligibility_profiles
        ],
        "included_workers": included_workers,
        "excluded_workers": excluded_workers
    }

    print(f"Inserting goal plan document: {goal_plan_document}")
    goal_plan_id = goal_plan_collection.insert_one(goal_plan_document).inserted_id
    new_goal_plan = goal_plan_collection.find_one({'_id': goal_plan_id})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])

    return jsonify(new_goal_plan), 201

@goal_plan_bp.route('/', methods=['GET'])
def get_goal_plans():
    goal_plans = list(goal_plan_collection.find())
    for goal_plan in goal_plans:
        goal_plan['_id'] = str(goal_plan['_id'])
    return jsonify(goal_plans), 200

@goal_plan_bp.route('/<goal_plan_name>', methods=['GET'])
def get_goal_plan(goal_plan_name):
    print(f"Fetching goal plan: {goal_plan_name}")
    goal_plan = goal_plan_collection.find_one({'details.goal_plan_name': goal_plan_name})
    if goal_plan:
        goal_plan['_id'] = str(goal_plan['_id'])
        return jsonify(goal_plan), 200
    else:
        print(f"Goal plan not found: {goal_plan_name}")
        return jsonify({'error': 'Goal plan not found'}), 404

@goal_plan_bp.route('/<goal_plan_name>', methods=['PUT'])
def update_goal_plan(goal_plan_name):
    data = lowercase_keys(request.json)
    print(f"Received data for updating goal plan: {data}")

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("details", {}).get("updated_by", "Unknown")
    data["details"]["updated_date"] = current_time
    data["details"]["updated_by"] = updated_by

    print(f"Updating goal plan: {goal_plan_name}")
    result = goal_plan_collection.update_one({'details.goal_plan_name': goal_plan_name}, {'$set': data})
    if result.matched_count:
        updated_goal_plan = goal_plan_collection.find_one({'details.goal_plan_name': goal_plan_name})
        updated_goal_plan['_id'] = str(updated_goal_plan['_id'])
        return jsonify(updated_goal_plan), 200
    else:
        print(f"Goal plan not found for update: {goal_plan_name}")
        return jsonify({'error': 'Goal plan not found'}), 404

@goal_plan_bp.route('/<goal_plan_name>', methods=['DELETE'])
def delete_goal_plan(goal_plan_name):
    print(f"Deleting goal plan: {goal_plan_name}")
    result = goal_plan_collection.delete_one({'details.goal_plan_name': goal_plan_name})
    if result.deleted_count:
        return jsonify({'message': 'Goal plan deleted successfully'}), 200
    else:
        print(f"Goal plan not found for deletion: {goal_plan_name}")
        return jsonify({'error': 'Goal plan not found'}), 404





