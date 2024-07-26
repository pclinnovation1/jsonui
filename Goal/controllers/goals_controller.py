from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

goals_bp = Blueprint('goals_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
employee_collection = db[config.EMPLOYEE_COLLECTION]
derived_employee_collection = db[config.DERIVED_EMPLOYEE_COLLECTION]
eligibility_profiles_collection = db[config.ELIGIBILITY_PROFILES_COLLECTION_NAME]

# Helper function to get matching employees based on eligibility name
def get_matching_employees(eligibility_name):
    eligibility_profile = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": eligibility_name})
    print(f"Eligibility Profile: {eligibility_profile}")
    
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
                    query[field_name] = value
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

@goals_bp.route('/', methods=['POST'])
def create_goal():
    data = request.json
    print(f"Received data: {data}")

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")
    print(f"Current time: {current_time}, Updated by: {updated_by}")

    goal= data.get("goal_name", {})
    print(f"Goal data: {goal}")

    eligibility_name = data.get("eligibility_name", "")
    employees = get_matching_employees(eligibility_name)

    data["employees"] = employees

    goal_id = goals_collection.insert_one(data).inserted_id
    new_goal = goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    print(f"Inserted new goal: {new_goal}")
    return jsonify(new_goal), 201

@goals_bp.route('/', methods=['GET'])
def get_goals():
    goals = list(goals_collection.find())
    for goal in goals:
        goal['_id'] = str(goal['_id'])
    print(f"Retrieved goals: {goals}")
    return jsonify(goals), 200

@goals_bp.route('/<goal_name>', methods=['GET'])
def get_goal(goal_name):
    goal = goals_collection.find_one({'goals.basic_info.goal_name': goal_name})
    if goal:
        goal['_id'] = str(goal['_id'])
        print(f"Retrieved goal: {goal}")
        return jsonify(goal), 200
    else:
        print(f"Goal not found: {goal_name}")
        return jsonify({'error': 'Goal not found'}), 404

@goals_bp.route('/<goal_name>', methods=['PUT'])
def update_goal(goal_name):
    data = request.json
    print(f"Received data for update: {data}")

    goal = data.get("goals", {})
    eligibility_name = goal.get("eligibility_name", "")
    employees = get_matching_employees(eligibility_name)
    goal["employees"] = employees

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")
    goal["updated_date"] = current_time
    goal["updated_by"] = updated_by

    data["goals"] = goal

    result = goals_collection.update_one({'goals.basic_info.goal_name': goal_name}, {'$set': data})
    if result.matched_count:
        updated_goal = goals_collection.find_one({'goals.basic_info.goal_name': goal_name})
        updated_goal['_id'] = str(updated_goal['_id'])
        print(f"Updated goal: {updated_goal}")
        return jsonify(updated_goal), 200
    else:
        print(f"Goal not found for update: {goal_name}")
        return jsonify({'error': 'Goal not found'}), 404











