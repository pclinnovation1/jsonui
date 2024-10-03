from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]

probation_blueprint = Blueprint('probation', __name__)

@probation_blueprint.route('/view', methods=['POST'])
def view_probation_period():
    data = request.get_json()
    person_name = data.get('person_name')

    if not person_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the employee details
    person = employee_details_collection.find_one({"person_name": person_name}, {"trial_period": 1, "trial_period_ends": 1})
    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Extract probationary period fields
    probationary_fields = {
        "trial_period": person.get("trial_period", ""),
        "trial_period_ends": person.get("trial_period_ends", "")
    }

    return jsonify(probationary_fields), 200


