from flask import request, jsonify, Blueprint
from pymongo import MongoClient
import config


# Establish connection to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]


change_manager_blueprint = Blueprint('change_manager', __name__)


def change_manager_details(employee_names, new_manager_name):
    """
    Update the manager name and person number for a list of employees after verifying the new manager exists in the collection.
    
    :param employee_names: The list of employee names whose manager needs to be updated.
    :param new_manager_name: The new manager's name.
    :return: Result of the update operation.
    """
    try:
        # Check if the new manager exists in the collection
        new_manager = collection.find_one({"person_name": new_manager_name})
        if not new_manager:
            return {"error": "New manager not found in the collection"}

        # Initialize a result summary
        result_summary = {
            "updated": [],
            "not_found": [],
            "failed": []
        }

        for person_name in employee_names:
            # Find the employee in the collection
            employee = collection.find_one({"person_name": person_name})
            if not employee:
                result_summary["not_found"].append(person_name)
                continue
            
            # Update the manager name and manager person number for the employee
            result = collection.update_one(
                {"person_name": person_name},
                {"$set": {
                    "manager_name": new_manager.get("person_name"),
                    "manager_person_number": new_manager.get("person_number")
                }}
            )
            
            if result.modified_count > 0:
                result_summary["updated"].append(person_name)
            else:
                result_summary["failed"].append(person_name)
        
        return result_summary
    
    except Exception as e:
        return {"error": str(e)}

@change_manager_blueprint.route('/update', methods=['POST'])
def change_manager_route():
    """
    Endpoint to change the manager details for a list of employees.
    """
    try:
        # Extract data from the request
        data = request.get_json()
        employee_names = data.get('employee_names')
        new_manager_name = data.get('new_manager_name')

        # Validate the input data
        if not employee_names or not isinstance(employee_names, list):
            return jsonify({"error": "employee_names must be a list"}), 400
        if not new_manager_name:
            return jsonify({"error": "new_manager_name is required"}), 400

        # Call the function to change manager details
        result = change_manager_details(employee_names, new_manager_name)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

