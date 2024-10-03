from flask import Flask, request, jsonify
from pymongo import MongoClient
from jsonschema import validate, ValidationError
from datetime import datetime
import config

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection setup  
MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

# Set up MongoDB client and database 
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# MongoDB collection
eligibility_profile_collection = db[config.JRN_eligibility_profiles]
employee_collection = db[config.HRM_employee_details]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data  # Base case: return the data if neither dict nor list

# Helper function to check if a field exists in the MongoDB collection
def field_exists(collection, field_name):
    return collection.find_one({field_name: {"$exists": True}}) is not None

# Function to construct a MongoDB query based on provided criteria
def construct_query(criteria, collection):
    query = {}
    for key, value in criteria.items():
        if isinstance(value, str):
            if value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()  # Ensure field names are lowercase
                if field_exists(collection, field_name):
                    query[field_name] = {"$regex": f"^{value}$", "$options": "i"}  # Case-insensitive regex match
        elif isinstance(value, (int, float, bool)):
            field_name = key.replace(' ', '_').lower()
            if field_exists(collection, field_name):
                query[field_name] = value
    return query

# Function to retrieve matching employees based on profile
def get_matching_employees(profile):
    matched_employees = set()
    criteria = profile["eligibility_criteria"]

    # Combine all criteria sections
    all_criteria = {
        **criteria.get("personal", {}),
        **criteria.get("employment", {}),
        **criteria.get("derived_factors", {}),
        **criteria.get("other", {}),
        **criteria.get("labor_relations", {}),
    }

    # Construct the query for employee details only (from employee_collection)
    query_for_employee_details = construct_query(all_criteria, employee_collection)

    # Fetch employees based on the constructed query
    employees = list(employee_collection.find(query_for_employee_details))
    
    # Get employee names
    employee_names_from_hrm = {employee.get('person_name') for employee in employees}
    
    # Update matched employees with the names retrieved from the employee collection
    matched_employees.update(employee_names_from_hrm)

    return list(matched_employees)

# def check_employee_eligibility_for_JRN(person_name, journey_name):
#     """
#     Function to check if an employee is eligible for a given journey based on multiple eligibility profiles.

#     Args:
#         person_name (str): Name of the employee to check eligibility for.
#         journey_name (str): Name of the journey for profile usage to check eligibility.

#     Returns:
#         bool: True if the employee is eligible, False otherwise.
#     """
#     # Fetch employee details from the employee collection
#     employee_data = employee_collection.find_one({"person_name": person_name})
    
#     if not employee_data:
#         print(f"Employee '{person_name}' not found.")
#         return False

#     # Convert ObjectId to string in employee_data
#     if '_id' in employee_data:
#         employee_data['_id'] = str(employee_data['_id'])

#     # Fetch all eligibility profiles for Journey type and specific journey or 'All'
#     profiles = eligibility_profile_collection.find({
#         "eligibility_profile_definition.profile_type": "journey",
#         "eligibility_profile_definition.profile_usage": journey_name
#     })

#     # If no profiles are found, assume eligibility is not restricted
   
   
#     profilecheck = list(profiles)

#     if len(profilecheck) == 0:
#         print(f"No eligibility profiles found for journey '{journey_name}'.")
#         return True

#     # Step 1: Create a set to hold all matching employees
#     matched_employees = set()

#     # Step 2: Loop through each profile and gather matching employees
#     print(profiles)
#     for profile in profiles:
#         print(profile)
#         profile_matching_employees = get_matching_employees(profile)
#         matched_employees.update(profile_matching_employees)  # Add to the set to merge results

#     # Step 3: Check if the employee is in the set of matching employees
#     return person_name in matched_employees


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

    # Fetch all eligibility profiles for Journey type and specific journey or 'All'
    profiles = eligibility_profile_collection.find({
        "eligibility_profile_definition.profile_type": "journey",  # Corrected profile type
        "eligibility_profile_definition.profile_usage": journey_name  # Use journey_name to match
    })
    
    # If no profiles are found, assume eligibility is not restricted
    profilecheck = list(profiles)
    if len(profilecheck) == 0:
        print(f"No eligibility profiles found for journey '{journey_name}'.")
        return True

    # Step 1: Create a set to hold all matching employees
    matched_employees = set()

    # Step 2: Loop through each profile and gather matching employees
    
    for profile in profilecheck:
        profile_matching_employees = get_matching_employees(profile)
        matched_employees.update(profile_matching_employees)  # Add to the set to merge results

    # Step 3: Check if the employee is in the set of matching employees
    
    return person_name in matched_employees


def check_employee_eligibility_for_task(person_name, task_name):
    """
    Function to check if an employee is eligible for a given task based on multiple eligibility profiles.

    Args:
        person_name (str): Name of the employee to check eligibility for.
        task_name (str): Name of the task for profile usage to check eligibility.

    Returns:
        bool: True if the employee is eligible, False otherwise.
    """
    # Fetch employee details from the employee collection
    employee_data = employee_collection.find_one({"person_name": person_name})
    
    if not employee_data:
        print(f"Employee '{person_name}' not found.")
        return False

    # Convert ObjectId to string in employee_data
    if '_id' in employee_data:
        employee_data['_id'] = str(employee_data['_id'])

    # Fetch all eligibility profiles for Journey Task type and specific task or 'All'
    profiles = eligibility_profile_collection.find({
        "eligibility_profile_definition.profile_type": "journey_task",
        "eligibility_profile_definition.profile_usage": task_name
    })

    # If no profiles are found, assume eligibility is not restricted
    
    profilecheck = list(profiles)
    if len(profilecheck) == 0:
        print(f"No eligibility profiles found for task '{task_name}'.")
        return True

    # Step 1: Create a set to hold all matching employees
    
    matched_employees = set()

    # Step 2: Loop through each profile and gather matching employees
    for profile in profilecheck:
        
        profile_matching_employees = get_matching_employees(profile)
        matched_employees.update(profile_matching_employees)  # Add to the set to merge results

    # Step 3: Check if the employee is in the set of matching employees
    return person_name in matched_employees


# Example usage:Ossi Aalto
# print(check_employee_eligibility_for_JRN("Mika Aalto","Badge Request"))
# print(check_employee_eligibility_for_JRN("Ossi Aalto","Badge Request"))
# print(check_employee_eligibility_for_task("Mika Aalto", "Oras Group - MT meetings"))
# print(check_employee_eligibility_for_task("Mika Aalto", "Strategy, mission, Oras group"))

