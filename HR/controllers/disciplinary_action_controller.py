from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config
from datetime import datetime
from bson import ObjectId

# MongoDB connection
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db[config.EMPLOYEE_DETAIL_COLLECTION_NAME]
disciplinary_actions_collection = db[config.DISPLINARY_COLLECTION_NAME]

disciplinary_blueprint = Blueprint('disciplinary', __name__)

@disciplinary_blueprint.route('/add', methods=['POST'])
def add_disciplinary_action():
    data = request.get_json()
    person_name = data.get('person_name')
    action = data.get('action')
    reason = data.get('reason')
    event_date = data.get('event_date')
    action_date = data.get('action_date')
    status = data.get('status', "active")
    details = data.get('details', "")
    created_at = datetime.utcnow().isoformat()

    if not person_name or not action or not reason or not event_date or not action_date or not status:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the employee exists in OD_oras_employee_details collection
    person = employee_details_collection.find_one({"person_name": person_name})
    if not person:
        return jsonify({"error": "Person not found in employee details collection"}), 404

    # Fetch manager's name if action_by is not provided
    action_by = data.get('action_by')
    if not action_by:
        action_by = person.get('manager_name', 'Unknown')

    # Insert the disciplinary action
    disciplinary_action = {
        "person_name": person_name,
        "action": action,
        "reason": reason,
        "event_date": event_date,
        "action_date": action_date,
        "action_by": action_by,
        "status": status,
        "details": details,
        "created_at": created_at,
        "employee_comments": [],
        "manager_comments": []
    }
    disciplinary_actions_collection.insert_one(disciplinary_action)
    return jsonify({"message": "Disciplinary action added successfully"}), 201

@disciplinary_blueprint.route('/view', methods=['POST'])
def view_disciplinary_actions():
    data = request.get_json()
    person_name = data.get('person_name')

    if not person_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Fetch the disciplinary actions
    actions = list(disciplinary_actions_collection.find({"person_name": person_name}))
    if not actions:
        return jsonify({"error": "No disciplinary actions found"}), 404

    for action in actions:
        action['_id'] = str(action['_id'])

    return jsonify(actions), 200

@disciplinary_blueprint.route('/update', methods=['POST'])
def update_disciplinary_action():
    data = request.get_json()
    person_name = data.get('person_name')
    reason = data.get('reason')
    update_fields = data.get('update_fields')

    if not person_name or not reason or not update_fields:
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure only allowed fields are updated
    allowed_fields = ['action', 'reason', 'event_date', 'action_date', 'details', 'status', 'action_by']
    update_fields = {k: v for k, v in update_fields.items() if k in allowed_fields}
    update_fields["created_at"] = datetime.utcnow().isoformat()

    # Check if the disciplinary action exists
    disciplinary_action = disciplinary_actions_collection.find_one({"person_name": person_name, "reason": reason})
    if not disciplinary_action:
        return jsonify({"error": "Disciplinary action not found"}), 404

    # Update the disciplinary action
    result = disciplinary_actions_collection.update_one(
        {"person_name": person_name, "reason": reason},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Action not found"}), 404

    return jsonify({"message": "Disciplinary action updated successfully", "updated_fields": len(update_fields)}), 200

@disciplinary_blueprint.route('/delete', methods=['POST'])
def delete_disciplinary_action():
    data = request.get_json()
    person_name = data.get('person_name')
    reason = data.get('reason')

    if not person_name or not reason:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the disciplinary action exists
    result = disciplinary_actions_collection.delete_one({"person_name": person_name, "reason": reason})

    if result.deleted_count == 0:
        return jsonify({"error": "Disciplinary action not found"}), 404

    return jsonify({"message": "Disciplinary action deleted successfully"}), 200

@disciplinary_blueprint.route('/comment/manager', methods=['POST'])
def add_manager_comment():
    data = request.get_json()
    person_name = data.get('person_name')
    action = data.get('action')
    reason = data.get('reason')
    manager_comment = data.get('manager_comment')

    if not person_name or not action or not reason or not manager_comment:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the disciplinary action exists
    disciplinary_action = disciplinary_actions_collection.find_one({"person_name": person_name, "action": action, "reason": reason})
    if not disciplinary_action:
        return jsonify({"error": "Disciplinary action not found"}), 404

    # Add the manager's comment
    update = {
        "$push": {"manager_comments": manager_comment},
        "$set": {"created_at": datetime.utcnow().isoformat()}
    }

    disciplinary_actions_collection.update_one(
        {"person_name": person_name, "action": action, "reason": reason},
        update
    )

    return jsonify({"message": "Manager comment added successfully"}), 200

@disciplinary_blueprint.route('/comment/person', methods=['POST'])
def add_employee_comment():
    data = request.get_json()
    person_name = data.get('person_name')
    action = data.get('action')
    reason = data.get('reason')
    employee_comment = data.get('employee_comment')

    if not person_name or not action or not reason or not employee_comment:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the disciplinary action exists
    disciplinary_action = disciplinary_actions_collection.find_one({"person_name": person_name, "action": action, "reason": reason})
    if not disciplinary_action:
        return jsonify({"error": "Disciplinary action not found"}), 404

    # Add the employee's comment
    update = {
        "$push": {"employee_comments": employee_comment},
        "$set": {"created_at": datetime.utcnow().isoformat()}
    }

    disciplinary_actions_collection.update_one(
        {"person_name": person_name, "action": action, "reason": reason},
        update
    )

    return jsonify({"message": "Employee comment added successfully"}), 200



