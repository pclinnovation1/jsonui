from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from jsonschema import validate, ValidationError
from datetime import datetime
import config

# Initialize Blueprint for goal plan
goal_plan_bp = Blueprint('goal_plan_bp', __name__)

# MongoDB connection setup
MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = config.DATABASE_NAME

# Set up MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# MongoDB collections
goal_plan_collection = db[config.COLLECTIONS["goal_plan_collection"]]
review_period_collection = db[config.COLLECTIONS["review_period_collection"]]
performance_document_types_collection = db[config.COLLECTIONS["performance_document_types_collection"]]
goals_collection = db[config.COLLECTIONS["goals_collection"]]
eligibility_profiles_collection = db[config.COLLECTIONS["eligibility_profiles_collection"]]
employee_details_collection = db[config.COLLECTIONS["employee_details_collection"]]
employee_personal_details_collection = db[config.COLLECTIONS["employee_personal_details_collection"]]
employee_salary_details_collection = db[config.COLLECTIONS["employee_salary_details_collection"]]

# HR or Manager Route to Create a New Goal Plan
# This route allows HR or managers to create a new goal plan in the `goal_plan_collection`.
# 1. The input data is validated against a predefined schema to ensure required fields are provided.
#    - The schema includes fields such as `goal_plan_name`, `review_period`, `performance_document_type`, and `eligibility_profiles`.
# 2. The route checks if the `review_period` and `performance_document_type` exist in their respective collections.
#    - If they are not found, an error is returned.
# 3. The route also validates that each goal in the `goals` list exists in the `goals_collection`.
#    - If a goal is not found, an error is returned.
# 4. Eligibility profiles are validated to ensure they exist, and the provided `included_workers` are checked against the `employee_details_collection`.
# 5. The new goal plan document is created, storing details such as `eligibility_profiles`, `goals`, and validated workers.
# 6. The goal plan is inserted into the `goal_plan_collection`, and its details are returned in the response with a status of 201 (Created).
# 7. it also check if a goal plan with the same goal_plan_name, review_period and performance_document_type already exists
@goal_plan_bp.route('/create', methods=['POST'])
def create_goal_plan():
    data = config.lowercase_keys(request.json)
 
    try:
        validate(instance=data, schema=config.schemagp)
    except ValidationError as e:
        return jsonify({"error": "Invalid input data", "message": str(e)}), 400
    


    # Check if a goal plan with the same goal_plan_name and review_period already exists
    goal_plan_exists = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('details').get('goal_plan_name'),
        "details.review_period": data.get('details').get('review_period'),
        "details.performance_document_type": data.get('details').get('performance_document_type')
    })
    
    if goal_plan_exists:
        return jsonify({"error": "A goal plan with this name, review period and performance_document_type already exists"}), 400

    
    review_period1 = review_period_collection.find_one({"review_period_name": data.get('details').get('review_period')})
    if not review_period1:
        return jsonify({"error": "review_period not found"}), 404
    
    performance_document_types_collection1 = performance_document_types_collection.find_one({"name": data.get('details').get('performance_document_type')})
    if not performance_document_types_collection1:
        return jsonify({"error": "performance_document_type not found"}), 404

    goal_plan_details = data.get("details", {})
    goals = data.get("goals", [])
    for goal1 in goals:
        goal1 = goals_collection.find_one({"basic_info.goal_name": goal1})
        if not goal1:
            return jsonify({"error": "goal not found in goal collection"}), 404 

    eligibility_profile_names = [profile["name"] for profile in data.get("eligibility_profiles", [])]
    included_workers = set(data.get("included_workers", []))
    excluded_workers = set(data.get("excluded_workers", []))

    # Validate provided eligibility profiles
    if eligibility_profile_names:
        for profile_name in eligibility_profile_names:
            profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
            if not profile_data:
                return jsonify({"error": f"Eligibility profile '{profile_name}' not found"}), 404

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")

    eligibility_profiles = []

    for profile_name in eligibility_profile_names:
        profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile_name})
        profile_data['_id'] = str(profile_data['_id'])
        eligibility_profiles.append({
            "name": profile_data["eligibility_profile_definition"]["name"],
            # "criteria": profile_data.get("eligibility_criteria", {})
        })

    # Validate included workers against the employee collection
    validated_included_workers = set()
    for worker in included_workers:
        worker_exists = employee_details_collection.find_one({'person_name': worker})
        if worker_exists:
            validated_included_workers.add(worker)
        else:
            print(f"Excluded worker not found in collections: {worker}")

    goal_plan_document = {
        "details": goal_plan_details,
        "goals": goals,
        "eligibility_profiles": eligibility_profiles,  # Store eligibility criteria instead of employees
        "included_workers": list(validated_included_workers),
        "excluded_workers": list(excluded_workers),
        "updated_by": updated_by,
        "updated_at": current_time
    }

    goal_plan_id = goal_plan_collection.insert_one(goal_plan_document).inserted_id
    new_goal_plan = goal_plan_collection.find_one({'_id': goal_plan_id})
    new_goal_plan['_id'] = str(new_goal_plan['_id'])

    return jsonify({"message": "Goal plan created successfully"}), 201

@goal_plan_bp.route('/overwrite_goal_plan_details_and_goals', methods=['POST'])
def overwrite_goal_plan_details_and_goals():
    data = config.lowercase_keys(request.json)

    required_fields = ["goal_plan_name", "review_period", "performance_document_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if a goal plan with the same goal_plan_name and review_period already exists
    goal_plan = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    
    if not goal_plan:
        return jsonify({"error": "A goal plan does not exist"}), 400

    update_data = {}

    # Fields to be updated directly in the 'details' dictionary
    details_fields = ['evaluation_type', 'goal_weights', 'start_date', 'end_date', 'description']

    for field in details_fields:
        if field in data:
            update_data[f'details.{field}'] = data.get(field)

    # Overwrite the goals array if provided in the request
    if 'goals' in data:
        update_data['goals'] = data.get('goals')

    # Always update 'updated_at'
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = data.get("updated_by", "Admin")

    # Perform the update
    result = goal_plan_collection.update_one(
        {
            "details.goal_plan_name": data.get('goal_plan_name'),
            "details.review_period": data.get('review_period'),
            "details.performance_document_type": data.get('performance_document_type')
        },
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "No goal plan was updated"}), 400

    return jsonify({
        "message": "Goal plan updated successfully"
    }), 200

# HR or Manager Route to Add Workers to an Existing Goal Plan
# This route allows HR or managers to add workers to an existing goal plan's `included_workers` or `excluded_workers` lists.
# 1. Required fields include `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the specified goal plan already exists in the `goal_plan_collection`.
#    - If no matching goal plan is found, an error is returned.
# 3. If `included_workers` or `excluded_workers` are provided, they are added to the respective lists without overwriting existing workers.
#    - Workers in the `included_workers` list are validated against the `employee_details_collection` to ensure they exist.
# 4. The `updated_at` and `updated_by` fields are automatically updated to reflect the current update.
# 5. The response includes the updated goal plan and a success message if the update is successful.
@goal_plan_bp.route('/add_workers_to_goal_plan', methods=['POST'])
def add_workers_to_goal_plan():
    data = config.lowercase_keys(request.json)

    required_fields = ["goal_plan_name", "review_period", "performance_document_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if a goal plan with the same goal_plan_name and review_period exists or not
    goal_plan = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    
    if not goal_plan:
        return jsonify({"error": "A goal plan with this name and review period does not exists"}), 400


    update_data = {}
    
    # Append to included_workers without overwriting existing ones
    if 'included_workers' in data:
        new_included_workers = set(data.get('included_workers', []))
        existing_included_workers = set(goal_plan.get('included_workers', []))

        validated_included_workers = set()
        for worker in new_included_workers:
            worker_exists = employee_details_collection.find_one({'person_name': worker})
            if worker_exists:
                validated_included_workers.add(worker)
            else:
                print(f"Included worker not found: {worker}")

        # Combine existing workers with new workers
        combined_included_workers = existing_included_workers.union(validated_included_workers)
        update_data['included_workers'] = list(combined_included_workers)

    # Append to excluded_workers without overwriting existing ones
    if 'excluded_workers' in data:
        new_excluded_workers = set(data.get('excluded_workers', []))
        existing_excluded_workers = set(goal_plan.get('excluded_workers', []))

        combined_excluded_workers = existing_excluded_workers.union(new_excluded_workers)
        update_data['excluded_workers'] = list(combined_excluded_workers)

    # Always update 'updated_at'
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = data.get("updated_by", "Admin")

    # Perform the update
    result = goal_plan_collection.update_one(
        {  "details.goal_plan_name": data.get('goal_plan_name'),
           "details.review_period": data.get('review_period'),
           "details.performance_document_type": data.get('performance_document_type')}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "No goal plan was updated"}), 400

    # Return the updated goal plan
    updated_goal_plan = goal_plan_collection.find_one({  "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    updated_goal_plan['_id'] = str(updated_goal_plan['_id'])  # Convert ObjectId to string for JSON response

    return jsonify({
        "message": "Workers added successfully"
    }), 200

# HR or Manager Route to Overwrite Workers in a Goal Plan
# This route allows HR or managers to update the `included_workers` and `excluded_workers` lists for an existing goal plan in the `goal_plan_collection`.
# 1. Required fields include `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the specified goal plan exists based on `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If the goal plan does not exist, an error is returned.
# 3. The `included_workers` and `excluded_workers` lists are overwritten (replaced) with the new lists provided in the request.
#    - Workers in the `included_workers` list are validated against the `employee_details_collection` to ensure they exist.
# 4. The `updated_at` and `updated_by` fields are automatically updated to reflect the current update.
# 5. The response confirms the success of the update operation if the goal plan was updated successfully.
@goal_plan_bp.route('/overwrite_workers_in_goal_plan', methods=['POST'])
def overwrite_workers_in_goal_plan():
    data = config.lowercase_keys(request.json)

    required_fields = ["goal_plan_name", "review_period", "performance_document_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if a goal plan with the same goal_plan_name and review_period already exists
    goal_plan = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    
    if not goal_plan:
        return jsonify({"error": "A goal plan not exists"}), 400

    update_data = {}

    # Overwrite included_workers
    if 'included_workers' in data:
        new_included_workers = set(data.get('included_workers', []))

        validated_included_workers = set()
        for worker in new_included_workers:
            worker_exists = employee_details_collection.find_one({'person_name': worker})
            if worker_exists:
                validated_included_workers.add(worker)
            else:
                print(f"Included worker not found: {worker}")

        update_data['included_workers'] = list(validated_included_workers)

    # Overwrite excluded_workers
    if 'excluded_workers' in data:
        new_excluded_workers = set(data.get('excluded_workers', []))
        update_data['excluded_workers'] = list(new_excluded_workers)

    # Always update 'updated_at'
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = data.get("updated_by", "Admin")

    # Perform the update
    result = goal_plan_collection.update_one(
        {"details.goal_plan_name": data.get('goal_plan_name'),
           "details.review_period": data.get('review_period'),
           "details.performance_document_type": data.get('performance_document_type')}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "No goal plan was updated"}), 400
    return jsonify({
        "message": "Workers updated successfully"
    }), 200

# HR or Manager Route to Add Eligibility Profiles to a Goal Plan
# This route allows HR or managers to add new eligibility profiles to an existing goal plan without overwriting existing profiles.
# 1. Required fields include `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the specified goal plan already exists based on `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If the goal plan does not exist, an error is returned.
# 3. The new eligibility profiles are validated against the `eligibility_profile_collection` to ensure they exist.
#    - The new profiles are combined with the existing ones without overwriting them.
# 4. The `updated_at` and `updated_by` fields are automatically updated to reflect the current update.
# 5. The response confirms the success of the update operation if the eligibility profiles were added successfully.
@goal_plan_bp.route('/add_eligibility_profiles_to_goal_plan', methods=['POST'])
def add_eligibility_profiles_to_goal_plan():
    data = config.lowercase_keys(request.json)

    required_fields = ["goal_plan_name", "review_period", "performance_document_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if a goal plan exists or not
    goal_plan = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    
    if not goal_plan:
        return jsonify({"error": "A goal plan not exists"}), 400


    update_data = {}

    # Append to eligibility_profiles without overwriting existing ones
    if 'eligibility_profiles' in data:
        new_eligibility_profiles = data.get('eligibility_profiles', [])
        existing_eligibility_profiles = goal_plan.get('eligibility_profiles', [])

        # Validate and filter eligibility profiles
        validated_profiles = []
        for profile in new_eligibility_profiles:
            profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile["name"]})
            if profile_data:
                validated_profiles.append({
                    "name": profile_data["eligibility_profile_definition"]["name"]
                })
            else:
                print(f"Eligibility profile '{profile['name']}' not found")

        # Combine existing profiles with new profiles
        combined_eligibility_profiles = {profile['name']: profile for profile in existing_eligibility_profiles}
        combined_eligibility_profiles.update({profile['name']: profile for profile in validated_profiles})

        update_data['eligibility_profiles'] = list(combined_eligibility_profiles.values())

    # Always update 'updated_at'
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = data.get("updated_by", "Admin")

    # Perform the update
    result = goal_plan_collection.update_one(
        {"details.goal_plan_name": data.get('goal_plan_name'),
           "details.review_period": data.get('review_period'),
           "details.performance_document_type": data.get('performance_document_type')}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "No goal plan was updated"}), 400

    return jsonify({
        "message": "Eligibility profiles added successfully"
    }), 200

# HR or Manager Route to Overwrite Eligibility Profiles in a Goal Plan
# This route allows HR or managers to overwrite the existing eligibility profiles in a goal plan with new profiles.
# 1. Required fields include `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If any of these fields are missing, the request will return an error.
# 2. The route checks if the specified goal plan exists based on `goal_plan_name`, `review_period`, and `performance_document_type`.
#    - If the goal plan does not exist, an error is returned.
# 3. The provided eligibility profiles are validated to ensure they exist in the `eligibility_profile_collection`.
#    - If any eligibility profile does not exist, an error is returned.
# 4. The `eligibility_profiles` are completely overwritten with the new validated profiles.
# 5. The `updated_at` and `updated_by` fields are automatically updated to reflect the current update.
# 6. The response confirms the success of the update operation if the eligibility profiles were successfully updated.
@goal_plan_bp.route('/overwrite_eligibility_profiles_in_goal_plan', methods=['POST'])
def overwrite_eligibility_profiles_in_goal_plan():
    data = config.lowercase_keys(request.json)

    required_fields = ["goal_plan_name", "review_period", "performance_document_type"]  # Define required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "Missing required fields", "missing": missing_fields}), 400

    # Check if a goal plan with the same goal_plan_name and review_period already exists
    goal_plan = goal_plan_collection.find_one({
        "details.goal_plan_name": data.get('goal_plan_name'),
        "details.review_period": data.get('review_period'),
        "details.performance_document_type": data.get('performance_document_type')
    })
    
    if not goal_plan:
        return jsonify({"error": "A goal plan not exists"}), 400


    update_data = {}

    # Overwrite eligibility_profiles
    if 'eligibility_profiles' in data:
        new_eligibility_profiles = data.get('eligibility_profiles', [])

        # Validate and filter eligibility profiles
        validated_profiles = []
        for profile in new_eligibility_profiles:
            profile_data = eligibility_profiles_collection.find_one({"eligibility_profile_definition.name": profile["name"]})
            if profile_data:
                validated_profiles.append({
                    "name": profile_data["eligibility_profile_definition"]["name"]
                })
            else:
                return jsonify({"error": f"Eligibility profile '{profile['name']}' not found"}), 404

        update_data['eligibility_profiles'] = validated_profiles

    # Always update 'updated_at'
    update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = data.get("updated_by", "Admin")

    # Perform the update
    result = goal_plan_collection.update_one(
        {"details.goal_plan_name": data.get('goal_plan_name'),
           "details.review_period": data.get('review_period'),
           "details.performance_document_type": data.get('performance_document_type')}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "No goal plan was updated"}), 400

    return jsonify({
        "message": "Eligibility profiles updated successfully"
    }), 200
