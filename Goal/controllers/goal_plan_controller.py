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
employee_collection = db[config.EMPLOYEE_COLLECTION]
derived_employee_collection = db[config.DERIVED_EMPLOYEE_COLLECTION]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

# Helper function to check if a field exists in the collection
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

# Modified get_matching_employees function
def get_matching_employees(profile):
    matched_employees = set()
    criteria = profile["eligibility_criteria"]
    all_criteria = {**criteria.get("personal", {}), **criteria.get("employment", {})}

    # Construct queries separately for each collection
    query_for_employee_details = construct_query(all_criteria, employee_collection)
    query_for_derived_employee_details = construct_query(all_criteria, derived_employee_collection)

    employees = list(employee_collection.find(query_for_employee_details))
    derived_employees = list(derived_employee_collection.find(query_for_derived_employee_details))

    # Intersect the two sets of employees to get the common ones
    employee_names_from_hrm = {employee.get('person_name') for employee in employees}
    employee_names_from_derived = {employee.get('person_name') for employee in derived_employees}
    common_employee_names = employee_names_from_hrm.intersection(employee_names_from_derived)

    matched_employees.update(common_employee_names)

    return list(matched_employees)

@goal_plan_bp.route('/', methods=['POST'])
def create_goal_plan():
    data = lowercase_keys(request.json)
    print(f"Received data for goal plan creation: {data}")

    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = set(data.get("included_workers", []))
    excluded_workers = set(data.get("excluded_workers", []))

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = goal_plan_details.get("updated_by", "Unknown")
    goal_plan_details["updated_date"] = current_time
    goal_plan_details["updated_by"] = updated_by

    eligibility_profiles = []
    combined_employees = set()

    for profile_name in eligibility_profile_names:
        print(f"Fetching eligibility profile: {profile_name}")
        profile_data = eligibility_profile_collection.find_one({"eligibility_profile_definition.name": profile_name})
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

    # Combine all eligible employees with included workers, then subtract excluded workers
    combined_employees.update(included_workers)
    combined_employees.difference_update(excluded_workers)

    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,
        "eligibility_profiles": eligibility_profiles,
        "included_workers": list(included_workers),
        "excluded_workers": list(excluded_workers),
        "combined_employees": list(combined_employees)
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
