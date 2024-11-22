from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from jsonschema import validate, ValidationError
# from algorithms.general_algo import get_database
from datetime import datetime

# Initialize Blueprint for eligibility plan  
eligible_plan_bp = Blueprint('eligible_plan_bp', __name__)
 
# MongoDB connection setup  
MONGODB_URI = "mongodb://localhost:27017/testing"
# oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "testing"
# "oras"

# Set up MongoDB client and database 
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]



# MongoDB collections
eb_employees = db["PGM_eb_employees"] 
eligibility_profile_collection = db["PGM_eligibility_profiles"]
employee_details_collection = db["HRM_employee_details"]
employee_personal_details_collection = db["HRM_personal_details"]
employee_salary_details_collection = db["HRM_salary_details"]
derived_employee_collection = db['HRM_employee_derived_details']
 
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
                field_name = key.replace(' ', '_').lower()       # Ensure field names are also lowercase
                
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

# Route to retrieve eligible employees based on eligibility profiles.
# This route helps identify which employees are eligible for the specified eligibility profiles.
# It handles POST requests, fetches the eligible employees, and stores them in MongoDB.
@eligible_plan_bp.route('/create', methods=['POST'])
def create_eligibility_plan():
    # Ensure all keys in the data are lowercase and formatted
    data = lowercase_keys(request.json)
 
    # Define JSON schema
    schema = {
        "type": "object",
        "properties": {
           
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
        "required": ["eligibility_profiles", "included_workers", "excluded_workers"]
    }
 
    # Validate input JSON against the schema
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid input data", "message": str(e)}), 400
 
 
 
    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = set(data.get("included_workers", []))
    excluded_workers = set(data.get("excluded_workers", []))
 
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
        "eligibility_profiles": eligibility_profiles,
        "included_workers": list(included_workers),
        "excluded_workers": list(excluded_workers),
        "combined_employees": list(combined_employees)
    }
 
    goal_plan_id = eb_employees.insert_one(goal_plan_document).inserted_id
    new_goal_plan = eb_employees.find_one({'_id': goal_plan_id})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])
 
    return jsonify(new_goal_plan), 201