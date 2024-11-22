from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from jsonschema import validate, ValidationError
# from algorithms.general_algo import get_database
from datetime import datetime

goal_plan_bp = Blueprint('goal_plan_bp', __name__)


MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
# MongoDB client setup
goal_plan_collection = db["PGM_goal_plan"]
review_period_collection = db["PGM_review_period"]
goals_collection = db["PGM_goal"]
eligibility_profile_collection = db["PGM_eligibility_profiles"]
employee_collection = db['HRM_employee_details']
derived_employee_collection = db['HRM_employee_derived_details']

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
            field_name = key.replace(' ', '_').lower()  # Ensure field names are also lowercase
            
            # Convert both field name and value to lowercase for case-insensitive matching
            if field_exists(collection, field_name):
                query[field_name] = {"$regex": f"^{value}$", "$options": "i"}  # Case-insensitive regex match

    return query


# Modified get_matching_employees function with case-insensitive matching
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

@goal_plan_bp.route('/create', methods=['POST'])
def create_goal_plan():
    data = lowercase_keys(request.json)
    # Define JSON schema
    schema = {
        "type": "object",
        "properties": {
            "details": {
                "type": "object",
                "properties": {
                    "goal_plan_name": {"type": "string"},
                    "review_period": {"type": "string"},
                    "description": {"type": "string"},
                    "allow_updates_to_goals_by": {"type": "string"},
                    "actions_for_workers_and_managers_on_hr_assigned_goals": {"type": "string"},
                    "performance_document_types": {"type": "string"},
                    "evaluation_type": {"type": "string"},
                    "goal_weights": {"type": "string"},
                    "maximum_goals_for_this_goal_plan": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"}
                },
                "required": ["goal_plan_name", "review_period", "description", "start_date", "end_date"]
            },
            "goals": {
                "type": "array",
                "items": {"type": "string"}
            },
            "eligibility_profiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "included_workers": {
                "type": "array",
                "items": {"type": "string"}
            },
            "excluded_workers": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["details", "goals", "eligibility_profiles", "included_workers", "excluded_workers"]
    }

    # Validate input JSON against the schema
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid input data", "message": str(e)}), 400
    review_period = review_period_collection.find_one({"review_period_name": data.get('details.review_period')})
    if not review_period:
            return jsonify({"error": "review_period not found"}), 404

    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    for goal1 in goals:
        goal1 = goals_collection.find_one({"basic_info.goal_name": goal1})
        if not goal1:
         return jsonify({"error": "goal not found in goal collection"}), 404 

    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = set(data.get("included_workers", []))
    excluded_workers = set(data.get("excluded_workers", []))

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")

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


    # First, validate included workers against the employee collection
    validated_included_workers = set()
    for worker in included_workers:
    # Check if the worker exists in either the employee collection
      worker_exists = employee_collection.find_one({'person_name': worker})
      if worker_exists:
        validated_included_workers.add(worker)
      else:
        print(f"Excluded worker not found in collections: {worker}")

    # Combine all eligible employees with validated included workers, then subtract excluded workers
    combined_employees.update(validated_included_workers)
    combined_employees.difference_update(excluded_workers)

    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,
        "eligibility_profiles": eligibility_profiles,
        "included_workers": list(included_workers),
        "excluded_workers": list(excluded_workers),
        "combined_employees": list(combined_employees),
        "updated_by":updated_by,
        "updated_at":current_time
    }

    # print(f"Inserting goal plan document: {goal_plan_document}")
    goal_plan_id = goal_plan_collection.insert_one(goal_plan_document).inserted_id
    new_goal_plan = goal_plan_collection.find_one({'_id': goal_plan_id})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])

    return jsonify(new_goal_plan), 201