# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# # MongoDB connection
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

# employment_blueprint = Blueprint('employment', __name__)

# employment_fields = [
#     "employment_status", "employment_type", "effective_start_date", "effective_end_date",
#     "department", "job_title", "job_code", "job_family", "employment_country",
#     "organization_unit", "location", "manager_name", "manager_person_number",
#     "organization_number", "regular_or_temporary", "employment_health_examination",
#     "latest_periodic_health_examination", "salary_basis", "salary_class",
#     "salary_effective_date", "overall_salary_per_month", "allowance", "benefits",
#     "fte", "base_salary", "legal_entity", "role", "roles_list", "worker_category",
#     "working_hours_per_week", "working_hours_type", "full_time_or_part_time"
# ]

# @employment_blueprint.route('/view', methods=['POST'])
# def view_employment_details():
#     data = request.get_json()
#     person_name = data.get('person_name')
#     fields = data.get('fields', ["all"])

#     if not person_name:
#         return jsonify({"error": "Missing required fields"}), 400

#     # Fetch the employee details
#     person = employee_details_collection.find_one({"person_name": person_name})
#     if not person:
#         return jsonify({"error": "Person not found"}), 404

#     # Extract specified fields or all fields if "all" is specified
#     if "all" in fields:
#         selected_fields = {field: person.get(field, "") for field in employment_fields}
#     else:
#         selected_fields = {field: person.get(field, "") for field in fields if field in employment_fields}

#     return jsonify(selected_fields), 200

























































from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

employment_blueprint = Blueprint('employment', __name__)

employment_fields = [
    "employment_status", "employment_type", "effective_start_date", "effective_end_date",
    "department", "job_title", "job_code", "job_family", "employment_country",
    "organization_unit", "location", "manager_name", "manager_person_number",
    "organization_number", "regular_or_temporary", "employment_health_examination",
    "latest_periodic_health_examination", "salary_basis", "salary_class",
    "salary_effective_date", "overall_salary_per_month", "allowance", "benefits",
    "fte", "base_salary", "legal_entity", "role", "roles_list", "worker_category",
    "working_hours_per_week", "working_hours_type", "full_time_or_part_time"
]

@employment_blueprint.route('/view', methods=['POST'])
def view_employment_details():
    data = request.get_json()
    person_name = data.get('person_name')
    fields = data.get('fields', ["all"])

    if not person_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the employee details
    person = employee_details_collection.find_one({"person_name": person_name})
    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Extract specified fields or all fields if "all" is specified
    if "all" in fields:
        selected_fields = {field: person.get(field, "") for field in employment_fields}
    else:
        selected_fields = {field: person.get(field, "") for field in fields if field in employment_fields}

    return jsonify(selected_fields), 200

@employment_blueprint.route('/update', methods=['POST'])
def update_employment_details():
    data = request.get_json()
    person_name = data.get('person_name')
    update_fields = data.get('update_fields')

    if not person_name or not update_fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure only employment fields are updated
    update_fields = {k: v for k, v in update_fields.items() if k in employment_fields}

    # Update the employee details
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Employment details updated successfully"}), 200

@employment_blueprint.route('/delete', methods=['POST'])
def delete_employment_details():
    data = request.get_json()
    person_name = data.get('person_name')
    fields = data.get('fields', ["all"])

    if not person_name or not fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Prepare the update document for deletion
    if "all" in fields:
        update_document = {"$unset": {field: "" for field in employment_fields}}
    else:
        update_document = {"$unset": {field: "" for field in fields if field in employment_fields}}

    # Delete the specified fields
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        update_document
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Selected fields deleted successfully"}), 200




