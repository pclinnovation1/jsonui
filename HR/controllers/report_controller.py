from flask import Flask, Blueprint, request, jsonify
from pymongo import MongoClient
import config

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

report_blueprint = Blueprint('report', __name__)

# List of personal report fields
personal_report_fields = [
    "person_number", "birth_name", "date_of_birth", "first_name", "last_name",
    "given_name", "gender", "nationality", "home_city", "home_country", "home_district",
    "home_email", "home_phone_number", "home_postal_code", "home_regin", "home_state",
    "home_street_address", "email", "emergency_email", "emergency_name", "emergency_phone",
    "manager_name", "manager_person_number", "person_name", "person_type", "place_of_birth",
    "username"
]

# List of compensation report fields
compensation_report_fields = [
    "bank_account", "base_salary", "allowance", "benefits", "currency",
    "overall_salary_per_month", "salary_basis", "salary_class", "salary_effective_date",
    "salary_reason", "tax_number", "cost_center_code"
]

@report_blueprint.route('/personal', methods=['POST'])
def view_personal_report():
    data = request.get_json()
    person_name = data.get('person_name')

    if not person_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the employee details
    person = employee_details_collection.find_one({"person_name": person_name}, {field: 1 for field in personal_report_fields})
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    # ## send email
    # queue_email = {
    #     "person_name":person_name,
        
    # }

    # Add default empty string for missing fields
    personal_report = {field: person.get(field, "") for field in personal_report_fields}

    return jsonify(personal_report), 200

@report_blueprint.route('/compensation', methods=['POST'])
def view_compensation_report():
    data = request.get_json()
    person_name = data.get('person_name')

    if not person_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the employee details
    person = employee_details_collection.find_one({"person_name": person_name}, {field: 1 for field in compensation_report_fields})
    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Add default empty string for missing fields
    compensation_report = {field: person.get(field, "") for field in compensation_report_fields}

    return jsonify(compensation_report), 200
















