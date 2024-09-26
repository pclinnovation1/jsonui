from flask import Flask, request, jsonify
from pymongo import MongoClient
from jsonschema import validate, ValidationError
from datetime import datetime
import config

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection setup
MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = config.DATABASE_NAME

# Set up MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

journey_collection = db[config.JRN_journey]
task_collection = db[config.JRN_task]
employee_collection = db[config.HRM_employee_details]
eligibility_profile_collection = db[config.eligibility_profile_collection]
employee_personal_details_collection=db[config.employee_personal_details_collection]
employee_salary_details_collection=db[config.employee_salary_details_collection]
derived_employee_collection=db[config.derived_employee_collection]


# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):    
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data  # Base case: return the data if neither dict nor list
    
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

 
    query_for_employee_details = construct_query(all_criteria, employee_collection)
    query_for_employee_personal_details = construct_query(all_criteria, employee_personal_details_collection)
    query_for_employee_salary_details = construct_query(all_criteria, employee_salary_details_collection)
    query_for_derived_employee_details = construct_query(all_criteria, derived_employee_collection)
 


    employees = list(employee_collection.find(query_for_employee_details))
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
    print(matched_employees)
    return list(matched_employees)

def check_employee_eligibility_for_JRN(person_name, journey_name):
    """
    Function to check if an employee is eligible for a given journey based on multiple eligibility profiles.

    Args:
        person_name (str): Name of the employee to check eligibility for.
        journey_name (str): Name of the journey for profile usage to check eligibility.

    Returns:
        bool: True if the employee is eligible, False otherwise.
    """
    # Fetch employee details from the employee collection
    employee_data = employee_collection.find_one({"person_name": person_name})
    if not employee_data:
        print(f"Employee '{person_name}' not found.")
        return False
    journey1 = journey_collection.find_one({"journey_name": journey_name})
    if not journey1:
     print(f"Journey '{journey_name}' not found.")
     return False

    # Fetch the eligibility profiles from the journey (skip if not present)
    eligibility_profile_names = journey1.get('eligibility_profiles', [])

    # If eligibility profiles are empty or None, skip eligibility check
    if not eligibility_profile_names:
        print("No eligibility profiles to check. Skipping eligibility.")
        return True  # or return another appropriate value based on your logic
    eligibility_profiles = []
    combined_employees = set()
    for profile_name in eligibility_profile_names:
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
    return person_name in combined_employees        

def check_employee_eligibility_for_task(person_name, journey_name, task_name):
    # Fetch employee details from the employee collection
    employee_data = employee_collection.find_one({"person_name": person_name})

    if not employee_data:
        print(f"Employee '{person_name}' not found.")
        return False

    # Fetch the journey from the journey collection
    journey1 = journey_collection.find_one({"journey_name": journey_name})

    if not journey1:
        print(f"Journey '{journey_name}' not found.")
        return False
    # Find the task by task_name
    task = next((task for task in journey1.get('tasks', []) if task.get('task_name') == task_name), None)

    if not task:
        print(f"Task '{task_name}' not found in journey '{journey_name}'.")
        return False
    # Fetch the eligibility profiles from the task (skip if not present)
    eligibility_profile_names = task.get('eligibility_profiles', [])
    # If eligibility profiles are empty or None, skip eligibility check
    if not eligibility_profile_names:
        print(f"No eligibility profiles for task '{task_name}'. Skipping eligibility check.")
        return True  # Skip eligibility check and assume employee is eligible if no profiles exist

    eligibility_profiles = []
    combined_employees = set()

    # Check each eligibility profile associated with the task
    for profile_name in eligibility_profile_names:
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

    # Check if the person is in the combined eligible employees set
    return person_name in combined_employees
