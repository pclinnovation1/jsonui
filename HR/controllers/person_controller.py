from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config



# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

person_info_blueprint = Blueprint('person_info', __name__)

# List of personal info fields
personal_info_fields = [
    "person_number", "person_name", "first_name", "last_name", "birth_name", "gender",
    "date_of_birth", "nationality", "place_of_birth", "email", "home_city", "home_country",
    "home_district", "home_email", "home_phone_number", "home_postal_code", "home_regin",
    "home_state", "home_street_address", "manager_name", "emergency_name", "emergency_phone",
    "emergency_email"
]

@person_info_blueprint.route('/view', methods=['POST'])
def view_personal_info():
    data = request.get_json()
    person_name = data.get('person_name')
    fields = data.get('fields')

    if not person_name or not fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the employee details
    if "all" in fields:
        projection = {field: 1 for field in personal_info_fields}
    else:
        projection = {field: 1 for field in fields if field in personal_info_fields}
        projection["person_name"] = 1  # Ensure person_name is always included

    person = employee_details_collection.find_one({"person_name": person_name}, projection)

    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Exclude MongoDB-specific fields
    person.pop('_id', None)

    return jsonify(person), 200

@person_info_blueprint.route('/update', methods=['POST'])
def update_personal_info():
    data = request.get_json()
    person_name = data.get('person_name')
    update_fields = data.get('update_fields')

    if not person_name or not update_fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure only personal info fields are updated
    update_fields = {k: v for k, v in update_fields.items() if k in personal_info_fields}

    # Update the employee details
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Personal info updated successfully"}), 200

@person_info_blueprint.route('/delete', methods=['POST'])
def delete_personal_info():
    data = request.get_json()
    person_name = data.get('person_name')
    fields = data.get('fields')

    if not person_name or not fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Prepare the update document for deletion
    if "all" in fields:
        update_document = {"$unset": {field: "" for field in personal_info_fields}}
    else:
        update_document = {"$unset": {field: "" for field in fields if field in personal_info_fields}}

    # Delete the specified fields
    result = employee_details_collection.update_one(
        {"person_name": person_name},
        update_document
    )

    if result.matched_count == 0:
        return jsonify({"error": "Person not found"}), 404

    return jsonify({"message": "Selected fields deleted successfully"}), 200






































