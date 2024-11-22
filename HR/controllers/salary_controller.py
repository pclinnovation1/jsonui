from flask import request, jsonify, Blueprint
from pymongo import MongoClient
from datetime import datetime
import config

salary_blueprint = Blueprint('salary', __name__)

# Establish connection to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db['OD_oras_employee_details']
salary_details_collection = db['salary_details']

# Helper function to combine month and year
def format_month_year(month, year):
    return f"{month} {year}"

# Create salary details
@salary_blueprint.route('/create_salary', methods=['POST'])
def create_salary_details():
    try:
        data = request.get_json()

        required_fields = ["person_name", "month", "year", "basic", "hra", "special_allowance", "gross_earnings", "pf", "professional_tax", "income_tax", "total_deductions", "net_pay"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Fetch employee details using person_name
        employee = employee_details_collection.find_one({"person_name": data["person_name"]})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Combine month and year
        month_year = format_month_year(data["month"], data["year"])

        # Check if salary details for the month and year already exist
        existing_salary_details = salary_details_collection.find_one({"person_name": employee["person_name"], "month_year": month_year})
        if existing_salary_details:
            return jsonify({"error": "Salary details for this month and year already exist"}), 400

        new_salary_details = {
            "person_name": employee["person_name"],
            "month_year": month_year,
            "basic": data["basic"],
            "hra": data["hra"],
            "special_allowance": data["special_allowance"],
            "gross_earnings": data["gross_earnings"],
            "pf": data["pf"],
            "professional_tax": data["professional_tax"],
            "income_tax": data["income_tax"],
            "total_deductions": data["total_deductions"],
            "net_pay": data["net_pay"]
        }

        salary_details_collection.insert_one(new_salary_details)
        return jsonify({"message": "Salary details added successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update salary details
@salary_blueprint.route('/update_salary', methods=['POST'])
def update_salary_details():
    try:
        data = request.get_json()

        required_fields = ["person_name", "month", "year"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Fetch employee details using person_name
        employee = employee_details_collection.find_one({"person_name": data["person_name"]})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Combine month and year
        month_year = format_month_year(data["month"], data["year"])

        # Check if salary details for the month and year exist
        existing_salary_details = salary_details_collection.find_one({"person_name": employee["person_name"], "month_year": month_year})
        if not existing_salary_details:
            return jsonify({"error": "Salary details for this month and year not found"}), 404

        update_data = {}
        optional_fields = ["basic", "hra", "special_allowance", "gross_earnings", "pf", "professional_tax", "income_tax", "total_deductions", "net_pay"]
        for field in optional_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        salary_details_collection.update_one({"person_name": employee["person_name"], "month_year": month_year}, {"$set": update_data})
        return jsonify({"message": "Salary details updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete salary details
@salary_blueprint.route('/delete_salary', methods=['POST'])
def delete_salary_details():
    try:
        data = request.get_json()

        required_fields = ["person_name", "month", "year"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Fetch employee details using person_name
        employee = employee_details_collection.find_one({"person_name": data["person_name"]})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Combine month and year
        month_year = format_month_year(data["month"], data["year"])

        # Check if salary details for the month and year exist
        result = salary_details_collection.delete_one({"person_name": employee["person_name"], "month_year": month_year})

        if result.deleted_count == 0:
            return jsonify({"error": "Salary details for this month and year not found"}), 404

        return jsonify({"message": "Salary details deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


