from flask import request, jsonify, Blueprint
from pymongo import MongoClient
from datetime import datetime
import config

policy_blueprint = Blueprint('policy', __name__)

# Establish connection to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
policies_collection = db['HRM_policies']
acknowledgments_collection = db['HRM_policy_acknowledgments']
employee_details_collection = db['OD_oras_employee_details']

@policy_blueprint.route('/add_policy', methods=['POST'])
def add_policy():
    try:
        data = request.get_json()

        required_fields = ["policy_name", "policy_text", "policy_description", "policy_type", "effective_start_date", "effective_end_date", "attachments", "reviewer_comments", "approval_status", "approval_date", "publication_date", "audience"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Check if policy with the same name already exists
        existing_policy = policies_collection.find_one({"policy_name": data["policy_name"]})
        if existing_policy:
            return jsonify({"error": "Policy with this name already exists"}), 400

        new_policy = {
            "policy_name": data["policy_name"],
            "policy_text": data["policy_text"],
            "policy_description": data["policy_description"],
            "policy_type": data["policy_type"],
            "effective_start_date": data["effective_start_date"],
            "effective_end_date": data["effective_end_date"],
            "attachments": data["attachments"],
            "reviewer_comments": data["reviewer_comments"],
            "approval_status": data["approval_status"],
            "approval_date": data["approval_date"],
            "publication_date": data["publication_date"],
            "audience": data["audience"],
            "update_history": []
        }

        policies_collection.insert_one(new_policy)
        return jsonify({"message": "Policy added successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/update_policy', methods=['POST'])
def update_policy():
    try:
        data = request.get_json()

        if "policy_name" not in data:
            return jsonify({"error": "Missing field: policy_name"}), 400

        policy_name = data["policy_name"]
        existing_policy = policies_collection.find_one({"policy_name": policy_name})

        if not existing_policy:
            return jsonify({"error": "Policy not found"}), 404

        if "updated_by" not in data:
            return jsonify({"error": "Missing updated_by field"}), 400

        updated_by = data["updated_by"]
        updater = employee_details_collection.find_one({"person_name": updated_by})
        if not updater:
            return jsonify({"error": "Updater not found"}), 404

        update_data = {}
        optional_fields = ["policy_text", "policy_description", "policy_type", "effective_start_date", "effective_end_date", "attachments", "reviewer_comments", "approval_status", "approval_date", "publication_date", "audience"]

        updated_fields = {}
        old_values = {}
        for field in optional_fields:
            if field in data:
                update_data[field] = data[field]
                updated_fields[field] = data[field]
                old_values[field] = existing_policy.get(field)

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        # Add update history
        update_history_entry = {
            "update_description": "Updated policy fields",
            "updated_by": updated_by,
            "updated_date": datetime.now().isoformat(),
            "old_values": old_values
        }
        update_data["update_history"] = existing_policy.get("update_history", []) + [update_history_entry]

        policies_collection.update_one({"policy_name": policy_name}, {"$set": update_data})
        return jsonify({"message": "Policy updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/delete_policy', methods=['POST'])
def delete_policy():
    try:
        data = request.get_json()
        policy_name = data.get("policy_name")

        if not policy_name:
            return jsonify({"error": "policy_name is required"}), 400

        result = policies_collection.delete_one({"policy_name": policy_name})

        if result.deleted_count == 0:
            return jsonify({"error": "Policy not found"}), 404

        return jsonify({"message": "Policy deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/acknowledge_policy', methods=['POST'])
def acknowledge_policy():
    try:
        data = request.get_json()
        policy_name = data.get("policy_name")
        person_name = data.get("person_name")
        acknowledgment_date = data.get("acknowledgment_date")
        comments = data.get("comments")

        if not policy_name or not person_name or not acknowledgment_date:
            return jsonify({"error": "policy_name, person_name, and acknowledgment_date are required"}), 400

        policy = policies_collection.find_one({"policy_name": policy_name})
        if not policy:
            return jsonify({"error": "Policy not found"}), 404

        employee = employee_details_collection.find_one({"person_name": person_name})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        acknowledgment = {
            "policy_name": policy_name,
            "person_name": person_name,
            "person_number": employee.get("person_number"),
            "acknowledgment_date": acknowledgment_date,
            "comments": comments
        }

        acknowledgments_collection.insert_one(acknowledgment)
        return jsonify({"message": "Policy acknowledgment recorded successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/view_policies', methods=['POST'])
def view_policies():
    try:
        data = request.get_json()
        policies = []

        # Fetch policies based on input criteria
        query = {}

        if "policy_name" in data:
            query["policy_name"] = data["policy_name"]
        if "policy_type" in data:
            query["policy_type"] = data["policy_type"]
        if "audience" in data:
            query["audience"] = data["audience"]

        policies = list(policies_collection.find(query))

        if not policies:
            return jsonify({"message": "No policies found"}), 404

        # Filter fields for employee view
        employee_view_policies = []
        for policy in policies:
            employee_view_policy = {
                "policy_name": policy.get("policy_name"),
                "policy_text": policy.get("policy_text"),
                "policy_description": policy.get("policy_description"),
                "policy_type": policy.get("policy_type"),
                "effective_start_date": policy.get("effective_start_date"),
                "effective_end_date": policy.get("effective_end_date"),
                "attachments": policy.get("attachments"),
                "audience": policy.get("audience")
            }
            employee_view_policies.append(employee_view_policy)

        return jsonify({"policies": employee_view_policies}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500









