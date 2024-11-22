# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# employee_collection = db['s_employeedetails_2']
# eligibility_profiles_collection = db['P_EligibilityProfiles']
# assign_performance_collection = db['P_assign_performance']

# # Function to find the eligibility profile by name with case-insensitive search
# def find_eligibility_profile_by_name(name):
#     print(f"Searching for eligibility profile with name: {name}")
#     profile = eligibility_profiles_collection.find_one(
#         {"$or": [
#             {"create_participant_profile.eligibility_profile_definition.name": name},
#             {"create_participant_profile.eligibility_profile_definition.Name": name}
#         ]}
#     )
#     print(f"Found eligibility profile: {profile}")
#     return profile

# # Modified get_matching_employees function (from your existing code)
# def get_matching_employees(eligibility_profiles):
#     matched_employees = set()
#     for profile in eligibility_profiles:
#         print("Profile structure:", profile)  # Debugging print statement
        
#         # Use a case-insensitive search for the key
#         create_participant_profile = profile.get("create_participant_profile") or profile.get("Create Participant Profile")
#         print(f"create_participant_profile: {create_participant_profile}")
        
#         if not create_participant_profile:
#             print("Error: 'create_participant_profile' key not found.")
#             continue
        
#         criteria = create_participant_profile.get("eligibility_criteria") or create_participant_profile.get("Eligibility Criteria")
#         print(f"criteria: {criteria}")
        
#         if not criteria:
#             print("Error: 'eligibility_criteria' key not found.")
#             continue
        
#         query = {}

#         # Construct query based on non-null criteria fields in Personal section
#         personal_criteria = criteria.get("personal", {}) or criteria.get("Personal", {})
#         print(f"personal_criteria: {personal_criteria}")
        
#         for key, value in personal_criteria.items():
#             if value and value.lower() not in ["n/a", "all"]:
#                 field_name = key.replace(' ', '_').lower()
#                 query[field_name] = value
#                 print(f"Added to query: {field_name} = {value}")

#         # Construct query based on non-null criteria fields in Employment section
#         employment_criteria = criteria.get("employment", {}) or criteria.get("Employment", {})
#         print(f"employment_criteria: {employment_criteria}")
        
#         for key, value in employment_criteria.items():
#             if value and value.lower() not in ["n/a", "all"]:
#                 field_name = key.replace(' ', '_').lower()
#                 query[field_name] = value
#                 print(f"Added to query: {field_name} = {value}")

#         print(f"Final query: {query}")

#         # Execute the query and find matching employees
#         employees = employee_collection.find(query)
#         for employee in employees:
#             full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
#             matched_employees.add(full_name)
#             print(f"Matched employee: {full_name}")

#     print(f"Final matched employees: {list(matched_employees)}")
#     return list(matched_employees)

# # New API route to assign performance based on eligibility profile
# @assign_performance_bp.route('/assign_performance', methods=['POST'])
# def assign_performance():
#     data = request.json
#     print(f"Input data: {data}")

#     performance_document_name = data.get('performance_document_name')
#     eligibility_profile_name = data.get('eligibility_profile_name')
#     include_names = set(data.get('include', []))  # Names to include
#     exclude_names = set(data.get('exclude', []))  # Names to exclude

#     print(f"Performance document name: {performance_document_name}")
#     print(f"Eligibility profile name: {eligibility_profile_name}")
#     print(f"Include names: {include_names}")
#     print(f"Exclude names: {exclude_names}")

#     if not performance_document_name or not eligibility_profile_name:
#         print("Error: Missing required parameters")
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Fetch the eligibility profile using a case-insensitive search
#     eligibility_profile = find_eligibility_profile_by_name(eligibility_profile_name)

#     if not eligibility_profile:
#         print(f"Error: No eligibility profile found for name: {eligibility_profile_name}")
#         return jsonify({"error": f"No eligibility profile found for name: {eligibility_profile_name}"}), 404

#     # Use the get_matching_employees function to find eligible employees
#     eligible_employees = set(get_matching_employees([eligibility_profile]))
#     print(f"Eligible employees: {eligible_employees}")

#     # Validate include and exclude names against the employee records
#     valid_include = set()
#     valid_exclude = set()

#     for name in include_names:
#         first_name, last_name = name.split(' ', 1)
#         employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
#         print(f"Checking include name: {name} - Found: {employee}")
#         if employee:
#             full_name = f"{employee['first_name']} {employee['last_name']}"
#             valid_include.add(full_name)

#     for name in exclude_names:
#         first_name, last_name = name.split(' ', 1)
#         employee = employee_collection.find_one({"first_name": first_name, "last_name": last_name})
#         print(f"Checking exclude name: {name} - Found: {employee}")
#         if employee:
#             full_name = f"{employee['first_name']} {employee['last_name']}"
#             valid_exclude.add(full_name)

#     # Determine the final lists for include, exclude, and combined_employees
#     final_include = eligible_employees.intersection(valid_include)  # Intersection with include list
#     print(f"Final include: {final_include}")

#     final_exclude = eligible_employees.intersection(valid_exclude)  # Intersection with exclude list
#     print(f"Final exclude: {final_exclude}")

#     combined_employees = eligible_employees.union(final_include).difference(final_exclude)  # Combined list
#     print(f"Combined employees: {combined_employees}")

#     # Prepare the data for insertion/updating in P_assign_performance
#     performance_data = {
#         "performance_document_name": performance_document_name,
#         "eligibility_profile": {
#             "profile_name": eligibility_profile_name,
#             "employees": list(eligible_employees),
#             "include": list(final_include),
#             "exclude": list(final_exclude),
#             "combined_employees": list(combined_employees)
#         }
#     }

#     print(f"Final performance data: {performance_data}")

#     # Insert or update the document in P_assign_performance collection
#     assign_performance_collection.update_one(
#         {"performance_document_name": performance_document_name, "eligibility_profile.profile_name": eligibility_profile_name},
#         {"$set": performance_data},
#         upsert=True
#     )

#     return jsonify({"message": "Performance document assigned successfully", "data": performance_data}), 200

# # Add this blueprint to your app.py
# # In your app.py, you will need to register this blueprint:
# # app.register_blueprint(assign_performance_bp, url_prefix='/assign_performance')






























# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# employee_collection = db['s_employeedetails_2']
# eligibility_profiles_collection = db['P_EligibilityProfiles']
# assign_performance_collection = db['P_assign_performance']

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
# @assign_performance_bp.route('/assign_performance', methods=['POST'])
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

#     # Ensure that valid_include is actually being added to eligible_employees
#     final_include = eligible_employees.intersection(valid_include)  # Corrected logic
#     final_exclude = eligible_employees.intersection(valid_exclude)  # Corrected logic

#     # Directly add valid_include to the combined employees and then remove valid_exclude
#     combined_employees = eligible_employees.union(valid_include)  # Start with eligible + include
#     combined_employees.difference_update(valid_exclude)  # Remove exclude

#     print(f"Final include: {final_include}")
#     print(f"Final exclude: {final_exclude}")
#     print(f"Combined employees: {combined_employees}")

#     # Prepare the data for insertion/updating in P_assign_performance
#     performance_data = {
#         "performance_document_name": performance_document_name,
#         "eligibility_profile": {
#             "profile_name": eligibility_profile_name,
#             "employees": list(eligible_employees),
#             "include": list(final_include),
#             "exclude": list(final_exclude),
#             "combined_employees": list(combined_employees)
#         }
#     }

#     print(f"Final performance data to be updated: {performance_data}")

#     # Insert or update the document in P_assign_performance collection
#     result = assign_performance_collection.update_one(
#         {"performance_document_name": performance_document_name, "eligibility_profile.profile_name": eligibility_profile_name},
#         {"$set": performance_data},
#         upsert=True
#     )

#     print(f"Update operation result: matched_count = {result.matched_count}, modified_count = {result.modified_count}")

#     return jsonify({"message": "Performance document assigned successfully", "data": performance_data}), 200

# # Add this blueprint to your app.py
# # In your app.py, you will need to register this blueprint:
# # app.register_blueprint(assign_performance_bp, url_prefix='/assign_performance')


















































# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# employee_collection = db['s_employeedetails_2']
# eligibility_profiles_collection = db['P_EligibilityProfiles']
# assign_performance_collection = db['P_assign_performance']

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
# @assign_performance_bp.route('/assign_performance', methods=['POST'])
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
#         "performance_document_name": performance_document_name,
#         "eligibility_profile": {
#             "profile_name": eligibility_profile_name,
#             "employees": list(eligible_employees),
#             "include": list(final_include),
#             "exclude": list(final_exclude),
#             "combined_employees": list(combined_employees)
#         }
#     }

#     print(f"Final performance data to be updated: {performance_data}")

#     # Insert or update the document in P_assign_performance collection
#     result = assign_performance_collection.update_one(
#         {"performance_document_name": performance_document_name, "eligibility_profile.profile_name": eligibility_profile_name},
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
employee_collection = db['s_employeedetails_2']
eligibility_profiles_collection = db['P_EligibilityProfiles']
assign_performance_collection = db['P_eligible_employee']

# Modified get_matching_employees function (from your existing code)
def get_matching_employees(eligibility_profiles):
    matched_employees = set()
    for profile in eligibility_profiles:
        create_participant_profile = profile.get("create_participant_profile") or profile.get("Create Participant Profile")
        if not create_participant_profile:
            print("Error: 'create_participant_profile' key not found.")
            continue
        
        criteria = create_participant_profile.get("eligibility_criteria") or create_participant_profile.get("Eligibility Criteria")
        if not criteria:
            print("Error: 'eligibility_criteria' key not found.")
            continue
        
        query = {}

        # Construct query based on non-null criteria fields in Personal section
        personal_criteria = criteria.get("personal", {}) or criteria.get("Personal", {})
        for key, value in personal_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()
                query[field_name] = value

        # Construct query based on non-null criteria fields in Employment section
        employment_criteria = criteria.get("employment", {}) or criteria.get("Employment", {})
        for key, value in employment_criteria.items():
            if value and value.lower() not in ["n/a", "all"]:
                field_name = key.replace(' ', '_').lower()
                query[field_name] = value

        # Execute the query and find matching employees
        employees = employee_collection.find(query)
        for employee in employees:
            full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
            matched_employees.add(full_name)

    return list(matched_employees)

# New API route to assign performance based on eligibility profile
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
        {"create_participant_profile.eligibility_profile_definition.name": eligibility_profile_name}
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
    final_include = valid_include  # Corrected logic
    final_exclude = eligible_employees.intersection(valid_exclude)  # Corrected logic

    # Combined employees logic: Add include names first, then remove exclude names
    combined_employees = eligible_employees.union(final_include)  # Start with eligible + include
    combined_employees.difference_update(final_exclude)  # Remove exclude

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
# app.register_blueprint(assign_performance_bp, url_prefix='/assign_performance')
