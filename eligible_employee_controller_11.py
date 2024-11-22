
# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# eligible_employee_bp = Blueprint('eligible_employee_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# employee_collection = db[config.EMPLOYEE_DETAILS_COLLECTION_NAME]
# eligibility_profiles_collection = db[config.ELIGIBILITY_PROFILE_COLLECTION_NAME]
# assign_performance_collection = db[config.ELIGIBLE_EMPLOYEE_COLLECTION]

# # Modified get_matching_employees function (from your existing code)
# def get_matching_employees(eligibility_profiles):
#     matched_employees = set()
#     for profile in eligibility_profiles:
#         create_participant_profile = profile.get("create_participant_profile") or profile.get("Create Participant Profile")
#         if not create_participant_profile:
#             print("Error: 'create_participant_profile' key not found.")
#             continue
        
#         criteria = create_participant_profile.get("eligibility_criteria") or create_participant_profile.get("Eligibility Criteria")
#         if not criteria:
#             print("Error: 'eligibility_criteria' key not found.")
#             continue
        
#         query = {}

#         # Construct query based on non-null criteria fields in Personal section
#         personal_criteria = criteria.get("personal", {}) or criteria.get("Personal", {})
#         for key, value in personal_criteria.items():
#             if value and value.lower() not in ["n/a", "all"]:
#                 field_name = key.replace(' ', '_').lower()
#                 query[field_name] = value

#         # Construct query based on non-null criteria fields in Employment section
#         employment_criteria = criteria.get("employment", {}) or criteria.get("Employment", {})
#         for key, value in employment_criteria.items():
#             if value and value.lower() not in ["n/a", "all"]:
#                 field_name = key.replace(' ', '_').lower()
#                 query[field_name] = value

#         # Execute the query and find matching employees
#         employees = employee_collection.find(query)
#         for employee in employees:
#             full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
#             matched_employees.add(full_name)

#     return list(matched_employees)

# # New API route to assign performance based on eligibility profile
# @eligible_employee_bp.route('/eligible_employee', methods=['POST'])
# def assign_performance():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')
#     eligibility_profile_name = data.get('eligibility_profile_name')
#     include_names = set(data.get('include', []))  # Names to include
#     exclude_names = set(data.get('exclude', []))  # Names to exclude

#     print(f"Received input data: {data}")
#     print(f"Include names: {include_names}")
#     print(f"Exclude names: {exclude_names}")

#     if not performance_document_name or not eligibility_profile_name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Fetch the eligibility profile from P_EligibilityProfiles based on the name
#     eligibility_profile = eligibility_profiles_collection.find_one(
#         {"create_participant_profile.eligibility_profile_definition.name": eligibility_profile_name}
#     )

#     if not eligibility_profile:
#         return jsonify({"error": f"No eligibility profile found for name: {eligibility_profile_name}"}), 404

#     # Use the get_matching_employees function to find eligible employees
#     eligible_employees = set(get_matching_employees([eligibility_profile]))
#     print(f"Eligible employees: {eligible_employees}")

#     # Validate include and exclude names against the employee records
#     valid_include = set()
#     valid_exclude = set()

#     for name in include_names:
#         first_name, last_name = name.split(' ', 1)
#         print(f"Checking if {first_name} {last_name} exists in the database for include list...")
#         employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
#         if employee:
#             full_name = f"{employee['first_name']} {employee['last_name']}"
#             print(f"Found {full_name} in the database, adding to valid_include.")
#             valid_include.add(full_name)
#         else:
#             print(f"{name} not found in the database, skipping.")

#     for name in exclude_names:
#         first_name, last_name = name.split(' ', 1)
#         print(f"Checking if {first_name} {last_name} exists in the database for exclude list...")
#         employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
#         if employee:
#             full_name = f"{employee['first_name']} {employee['last_name']}"
#             print(f"Found {full_name} in the database, adding to valid_exclude.")
#             valid_exclude.add(full_name)
#         else:
#             print(f"{name} not found in the database, skipping.")

#     print(f"Valid include names: {valid_include}")
#     print(f"Valid exclude names: {valid_exclude}")

#     # Final include set is valid_include, regardless of eligible_employees
#     final_include = valid_include  # Corrected logic
#     final_exclude = eligible_employees.intersection(valid_exclude)  # Corrected logic

#     # Combined employees logic: Add include names first, then remove exclude names
#     combined_employees = eligible_employees.union(final_include)  # Start with eligible + include
#     combined_employees.difference_update(final_exclude)  # Remove exclude

#     print(f"Final include: {final_include}")
#     print(f"Final exclude: {final_exclude}")
#     print(f"Combined employees: {combined_employees}")

#     # Prepare the data for insertion/updating in P_assign_performance
#     performance_data = {
#         "profile_name": eligibility_profile_name,
#         "employees": list(eligible_employees),
#         "include": list(final_include),
#         "exclude": list(final_exclude),
#         "combined_employees": list(combined_employees),
#         "performance_document_name": performance_document_name
#     }

#     print(f"Final performance data to be updated: {performance_data}")

#     # Insert or update the document in P_assign_performance collection
#     result = assign_performance_collection.update_one(
#         {"performance_document_name": performance_document_name, "profile_name": eligibility_profile_name},
#         {"$set": performance_data},
#         upsert=True
#     )

#     print(f"Update operation result: matched_count = {result.matched_count}, modified_count = {result.modified_count}")

#     return jsonify({"message": "Performance document assigned successfully", "data": performance_data}), 200

# # Add this blueprint to your app.py
# # In your app.py, you will need to register this blueprint:
# # app.register_blueprint(assign_performance_bp, url_prefix='/assign_performance')


















































from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config
from bson import ObjectId

# Define the Blueprint
eligible_employee_bp = Blueprint('eligible_employee_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_collection = db[config.EMPLOYEE_DETAILS_COLLECTION_NAME]  # Collection 1
derived_employee_collection = db["HRM_employee_derived_details"]  # Collection 2
eligibility_profiles_collection = db[config.ELIGIBILITY_PROFILE_COLLECTION_NAME]
assign_performance_collection = db[config.ELIGIBLE_EMPLOYEE_COLLECTION]

def get_matching_employees(eligibility_profiles):
    matched_employees = set()
    
    for profile in eligibility_profiles:
        eligibility_criteria = profile.get("eligibility_criteria")
        if not eligibility_criteria:
            print("Error: 'eligibility_criteria' key not found.")
            continue

        # Build query for the employee_collection (Collection 1)
        query_employee_collection = {}
        personal_criteria = eligibility_criteria.get("personal", {})
        employment_criteria = eligibility_criteria.get("employment", {})

        for key, value in {**personal_criteria, **employment_criteria}.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()
                query_employee_collection[field_name] = value

        # Build query for the derived_employee_collection (Collection 2)
        query_derived_collection = {}
        derived_criteria = eligibility_criteria.get("derived_factors", {})
        other_criteria = eligibility_criteria.get("other", {})
        labor_relations_criteria = eligibility_criteria.get("labor_relations", {})

        for key, value in {**derived_criteria, **other_criteria, **labor_relations_criteria}.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()
                query_derived_collection[field_name] = value

        # Fetch employees from the employee_collection (Collection 1)
        employees = employee_collection.find(query_employee_collection)

        for employee in employees:
            person_name = employee.get("person_name")
            if not person_name:
                continue

            # Fetch the corresponding derived details from the derived_employee_collection (Collection 2)
            derived_employee = derived_employee_collection.find_one({"person_name": person_name})
            if not derived_employee:
                continue

            # Check if the derived details match the criteria
            derived_match = all(
                derived_employee.get(key.replace(' ', '_').lower()) == value 
                for key, value in query_derived_collection.items()
            )

            if derived_match:
                full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
                matched_employees.add(full_name)

    return list(matched_employees)

@eligible_employee_bp.route('/eligible_employee', methods=['POST'])
def assign_performance():
    data = request.json
    performance_document_name = data.get('performance_document_name')
    eligibility_profile_name = data.get('eligibility_profile_name')
    include_names = set(data.get('include', []))  # Names to include
    exclude_names = set(data.get('exclude', []))  # Names to exclude

    print(f"Received input data: {data}")
    print(f"Include names: {include_names}")
    print(f"Exclude names: {exclude_names}")

    if not performance_document_name or not eligibility_profile_name:
        return jsonify({"error": "Missing required parameters"}), 400

    # Fetch the eligibility profile from P_EligibilityProfiles based on the name
    eligibility_profile = eligibility_profiles_collection.find_one(
        {"eligibility_profile_definition.name": eligibility_profile_name}
    )

    if not eligibility_profile:
        return jsonify({"error": f"No eligibility profile found for name: {eligibility_profile_name}"}), 404

    # Use the get_matching_employees function to find eligible employees
    eligible_employees = set(get_matching_employees([eligibility_profile]))
    print(f"Eligible employees: {eligible_employees}")

    # Validate include and exclude names against the employee records
    valid_include = set()
    valid_exclude = set()

    for name in include_names:
        first_name, last_name = name.split(' ', 1)
        print(f"Checking if {first_name} {last_name} exists in the database for include list...")
        employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
        if employee:
            full_name = f"{employee['first_name']} {employee['last_name']}"
            print(f"Found {full_name} in the database, adding to valid_include.")
            valid_include.add(full_name)
        else:
            print(f"{name} not found in the database, skipping.")

    for name in exclude_names:
        first_name, last_name = name.split(' ', 1)
        print(f"Checking if {first_name} {last_name} exists in the database for exclude list...")
        employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
        if employee:
            full_name = f"{employee['first_name']} {employee['last_name']}"
            print(f"Found {full_name} in the database, adding to valid_exclude.")
            valid_exclude.add(full_name)
        else:
            print(f"{name} not found in the database, skipping.")

    print(f"Valid include names: {valid_include}")
    print(f"Valid exclude names: {valid_exclude}")

    # Final include set is valid_include, regardless of eligible_employees
    final_include = valid_include
    final_exclude = eligible_employees.intersection(valid_exclude)

    # Combined employees logic: Add include names first, then remove exclude names
    combined_employees = eligible_employees.union(final_include)
    combined_employees.difference_update(final_exclude)

    print(f"Final include: {final_include}")
    print(f"Final exclude: {final_exclude}")
    print(f"Combined employees: {combined_employees}")

    # Prepare the data for insertion/updating in P_assign_performance
    performance_data = {
        "profile_name": eligibility_profile_name,
        "employees": list(eligible_employees),
        "include": list(final_include),
        "exclude": list(final_exclude),
        "combined_employees": list(combined_employees),
        "performance_document_name": performance_document_name
    }

    print(f"Final performance data to be updated: {performance_data}")

    # Insert or update the document in P_assign_performance collection
    result = assign_performance_collection.update_one(
        {"performance_document_name": performance_document_name, "profile_name": eligibility_profile_name},
        {"$set": performance_data},
        upsert=True
    )

    print(f"Update operation result: matched_count = {result.matched_count}, modified_count = {result.modified_count}")

    return jsonify({"message": "Performance document assigned successfully", "data": performance_data}), 200

# Add this blueprint to your app.py
# In your app.py, you will need to register this blueprint:
# app.register_blueprint(eligible_employee_bp, url_prefix='/assign_performance')
