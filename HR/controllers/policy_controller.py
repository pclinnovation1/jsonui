from flask import request, jsonify,Blueprint
from pymongo import MongoClient
from datetime import datetime

policy_blueprint = Blueprint('policy', __name__)

# Establish connection to MongoDB
client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")
db = client["PCL_Interns"]
policies_collection = db['HRM_policies']
acknowledgments_collection = db['HRM_policy_acknowledgments']
violations_collection = db['HRM_policy_violations']
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

        update_data = {}
        optional_fields = ["policy_text", "policy_description", "policy_type", "effective_start_date", "effective_end_date", "attachments", "reviewer_comments", "approval_status", "approval_date", "publication_date", "audience"]

        for field in optional_fields:
            if field in data:
                update_data[field] = data[field]

        if "update_description" in data and "updated_by" in data and "updated_date" in data:
            update_history_entry = {
                "update_description": data["update_description"],
                "updated_by": data["updated_by"],
                "updated_date": data["updated_date"]
            }
            update_data["update_history"] = existing_policy.get("update_history", []) + [update_history_entry]
        elif "update_description" in data or "updated_by" in data or "updated_date" in data:
            return jsonify({"error": "Missing update history fields"}), 400

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

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

@policy_blueprint.route('/report_policy_violation', methods=['POST'])
def report_policy_violation():
    try:
        data = request.get_json()

        required_fields = ["violation_name", "violators", "policy_name", "violation_date", "violation_description", "reporter_name", "evidence"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        violators_info = []
        for violator in data["violators"]:
            employee = employee_details_collection.find_one({"person_name": violator})
            if not employee:
                return jsonify({"error": f"Violator not found: {violator}"}), 404
            violators_info.append({"person_name": violator, "person_number": employee.get("person_number")})

        reporter = employee_details_collection.find_one({"person_name": data["reporter_name"]})
        if not reporter:
            return jsonify({"error": "Reporter not found"}), 404

        new_violation = {
            "violation_name": data["violation_name"],
            "violators": violators_info,
            "policy_name": data["policy_name"],
            "violation_date": data["violation_date"],
            "violation_description": data["violation_description"],
            "reporter_name": data["reporter_name"],
            "reporter_number": reporter.get("person_number"),
            "evidence": data["evidence"],
            "status": "Reported"
        }

        violations_collection.insert_one(new_violation)
        return jsonify({"message": "Policy violation reported successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/update_violation_investigation', methods=['POST'])
def update_violation_investigation():
    try:
        data = request.get_json()

        required_fields = ["violation_name", "investigation_start_date", "investigation_end_date", "investigation_findings"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        violation_name = data["violation_name"]
        existing_violation = violations_collection.find_one({"violation_name": violation_name})

        if not existing_violation:
            return jsonify({"error": "Violation not found"}), 404

        update_data = {
            "investigation_start_date": data["investigation_start_date"],
            "investigation_end_date": data["investigation_end_date"],
            "investigation_findings": data["investigation_findings"],
            "status": "Investigated"
        }

        violations_collection.update_one({"violation_name": violation_name}, {"$set": update_data})
        return jsonify({"message": "Investigation details updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/update_disciplinary_action', methods=['POST'])
def update_disciplinary_action():
    try:
        data = request.get_json()

        required_fields = ["violation_name", "disciplinary_action_type", "action_date", "action_description", "action_taken_by", "compliance_status"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        violation_name = data["violation_name"]
        existing_violation = violations_collection.find_one({"violation_name": violation_name})

        if not existing_violation:
            return jsonify({"error": "Violation not found"}), 404

        update_data = {
            "disciplinary_action_type": data["disciplinary_action_type"],
            "action_date": data["action_date"],
            "action_description": data["action_description"],
            "action_taken_by": data["action_taken_by"],
            "compliance_status": data["compliance_status"],
            "status": "Action Taken"
        }

        violations_collection.update_one({"violation_name": violation_name}, {"$set": update_data})
        return jsonify({"message": "Disciplinary action details updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/acknowledge_violation', methods=['POST'])
def acknowledge_violation():
    try:
        data = request.get_json()

        required_fields = ["violation_name", "acknowledgment_date", "acknowledgment_status", "status"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        violation_name = data["violation_name"]
        existing_violation = violations_collection.find_one({"violation_name": violation_name})

        if not existing_violation:
            return jsonify({"error": "Violation not found"}), 404

        update_data = {
            "acknowledgment_date": data["acknowledgment_date"],
            "acknowledgment_status": data["acknowledgment_status"],
            "status": data["status"]
        }

        violations_collection.update_one({"violation_name": violation_name}, {"$set": update_data})
        return jsonify({"message": "Violation acknowledgment recorded successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@policy_blueprint.route('/view_policies', methods=['POST'])
def view_policies():
    try:
        data = request.get_json()
        policies = []

        # Fetch policies based on input criteria
        if "policy_name" in data:
            policy_name = data["policy_name"]
            policy = policies_collection.find_one({"policy_name": policy_name, "audience": "employee"})
            if policy:
                policies.append(policy)
        elif "policy_type" in data:
            policy_type = data["policy_type"]
            policies = list(policies_collection.find({"policy_type": policy_type, "audience": "employee"}))
        else:
            # Fetch all policies where audience includes "employee"
            policies = list(policies_collection.find({"audience": "employee"}))

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


