
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

    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = validate_employee_full_names(data.get("included_workers", []))
    excluded_workers = validate_employee_full_names(data.get("excluded_workers", []))
    goal_plan_name = goal_plan_details.get("goal_plan_name", "")

    eligibility_profiles = []
    matched_employees = {}

    for profile_name in eligibility_profile_names:
        profile_data = eligibility_profile_collection.find_one({"create_participant_profile.eligibility_profile_definition.name": profile_name})
        if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligibility_profiles.append(profile_data)
            matched_employees[profile_name] = get_matching_employees([profile_data])

    for profile_name in matched_employees:
        matched_employees[profile_name] = [emp for emp in matched_employees[profile_name] if emp not in excluded_workers]

    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,
        "eligibility_profiles": [
            {
                "name": ep["create_participant_profile"]["eligibility_profile_definition"]["name"],
                "employees_name": list(matched_employees[ep["create_participant_profile"]["eligibility_profile_definition"]["name"]])
            }
            for ep in eligibility_profiles
        ],
        "included_workers": included_workers,
        "excluded_workers": excluded_workers
    }

    goal_plan_id = goal_plan_collection.insert_one(goal_plan_document).inserted_id
    new_goal_plan = goal_plan_collection.find_one({'_id': ObjectId(goal_plan_id)})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])

    return jsonify(new_goal_plan), 201

@goal_plan_bp.route('/', methods=['GET'])
def get_goal_plans():
    goal_plans = list(goal_plan_collection.find())
    for goal_plan in goal_plans:
        goal_plan['_id'] = str(goal_plan['_id'])
    return jsonify(goal_plans), 200

@goal_plan_bp.route('/<goal_plan_id>', methods=['GET'])
def get_goal_plan(goal_plan_id):
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
