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
employee_collection = db['s_employeedetails_1']
include_exclude_collection = db[config.INCLUDE_EXCLUDE_COLLECTION_NAME]

# Modified get_matching_employees function
def get_matching_employees(eligibility_profiles):
    matched_employees = set()
    for profile in eligibility_profiles:
        print("profile:, ", profile)
        print()
        criteria = profile["Create Participant Profile"]["Eligibility Criteria"]
        print("criteria:, ", criteria)
        print()
        query = {}

        # Construct query based on non-null criteria fields in Personal section
        personal_criteria = criteria.get("Personal", {})
        print("personal_criteria:, ", personal_criteria)
        print()
        for key, value in personal_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        # Construct query based on non-null criteria fields in Employment section
        employment_criteria = criteria.get("Employment", {})
        for key, value in employment_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_')
                query[field_name] = value

        # Print the constructed query for debugging
        print(f"Constructed Query: {query}")
        print()

        employees = employee_collection.find(query)
        for employee in employees:
            matched_employees.add(employee["Person_Number"])

        # Print the matched employees for debugging
        print(f"Matched Employees for profile {profile['Create Participant Profile']['Eligibility Profile Definition']['Name']}: {list(matched_employees)}")

    return list(matched_employees)

@goal_plan_bp.route('/', methods=['POST'])
def create_goal_plan():
    data = request.json

    # Extract the details from the input
    goal_plan_details = data.get("details", {})
    goal_names = [goal["goal_name"] for goal in data.get("goals", [])]
    eligibility_profile_names = [profile["Name"] for profile in data.get("eligibility_profiles", [])]
    goal_plan_name = goal_plan_details.get("Goal Plan Name", "")

    # Retrieve corresponding goals from the goal collection by name
    goals = list(goals_collection.find({"Goals.Basic Info.Goal Name": {"$in": goal_names}}))
    for goal in goals:
        goal['_id'] = str(goal['_id'])

    # Retrieve corresponding eligibility profiles from the eligibility profile collection by name
    eligibility_profiles = []
    for profile_name in eligibility_profile_names:
        profile_data = eligibility_profile_collection.find_one({"Create Participant Profile.Eligibility Profile Definition.Name": profile_name})
        if profile_data:
            profile_data['_id'] = str(profile_data['_id'])
            eligibility_profiles.append(profile_data)

    print(eligibility_profiles)

    # Get matching employees based on eligibility profiles
    matched_employees = get_matching_employees(eligibility_profiles)

    # Retrieve include/exclude information based on goal plan name
    include_exclude = include_exclude_collection.find_one({'goal_plan_name': goal_plan_name})
    if include_exclude:
        include_exclude['_id'] = str(include_exclude['_id'])

    # Create the goal plan document
    goal_plan_document = {
        "details": goal_plan_details,
        "goals": [{"goal_name": goal['Goals']['Basic Info']['Goal Name']} for goal in goals],
        "eligibility_profiles": [{"Name": ep["Create Participant Profile"]["Eligibility Profile Definition"]["Name"], "Employee_Id": matched_employees} for ep in eligibility_profiles],
        "include_exclude": include_exclude
    }

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
    data = request.json
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
