from flask import Flask, Blueprint, request, jsonify
from pymongo import MongoClient
import config

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

organizational_chart_blueprint = Blueprint('organizational_chart', __name__)

# List of organizational chart fields
organizational_chart_fields = [
    "business_unit", "cost_centre", "cost_centre_code", "department", "job_code",
    "job_family", "job_title", "legal_entity", "local_job_code", "location",
    "manager_name", "manager_person_number", "organization_number", "organization_unit",
    "parent_unit", "roles_list", "team_manager", "tk10_code", "working_as_manager",
    "business_title"
]

@organizational_chart_blueprint.route('/view', methods=['POST'])
def view_organizational_chart():
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
        selected_fields = {field: person.get(field, "") for field in organizational_chart_fields}
    else:
        selected_fields = {field: person.get(field, "") for field in fields if field in organizational_chart_fields}

    return jsonify(selected_fields), 200

@organizational_chart_blueprint.route('/update', methods=['POST'])
def update_organizational_chart():
    data = request.get_json()
    person_name = data.get('person_name')
    update_fields = data.get('update_fields')

    if not person_name or not update_fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure only organizational chart fields are updated
    update_fields = {k: v for k, v in update_fields.items() if k in organizational_chart_fields}

    # Update the employee details
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Organizational chart updated successfully"}), 200

@organizational_chart_blueprint.route('/delete', methods=['POST'])
def delete_organizational_chart():
    data = request.get_json()
    person_name = data.get('person_name')
    fields = data.get('fields', ["all"])

    if not person_name or not fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Prepare the update document for deletion
    if "all" in fields:
        update_document = {"$unset": {field: "" for field in organizational_chart_fields}}
    else:
        update_document = {"$unset": {field: "" for field in fields if field in organizational_chart_fields}}

    # Delete the specified fields
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        update_document
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Selected fields deleted successfully"}), 200


