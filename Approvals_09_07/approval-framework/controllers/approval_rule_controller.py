

from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId

approval_rule_bp = Blueprint('approval_rules', __name__)

@approval_rule_bp.route('/approval_rules', methods=['POST'])
def add_approval_rule():
    data = request.get_json()
    
    # Validate input data
    if not data:
        return jsonify({"message": "Invalid input"}), 400
    
    process_name = data.get('processName')
    if not process_name:
        return jsonify({"message": "processName is required"}), 400
    
    condition_refs = data.get('conditions')
    if not condition_refs:
        return jsonify({"message": "conditions are required"}), 400

    # Fetch the conditions for the given processName from the conditions collection
    condition_document = current_app.mongo.db.conditions.find_one({"processName": process_name})
    if not condition_document:
        return jsonify({"message": "Conditions not found for the given processName"}), 404

    conditions = condition_document['conditions']

    # Prepare the new rules using the conditions array indices
    new_rules = []
    for condition_ref in condition_refs:
        condition_index = int(condition_ref['conditionId'].split('[')[1][:-1])
        condition_data = conditions[condition_index]  # Fetch the condition using the index
        approvers = condition_ref['approvers']
        
        new_rule = {
            "condition": condition_data,
            "approvers": approvers
        }
        new_rules.append(new_rule)

    # Check if the approval rule already exists
    approval_rule = current_app.mongo.db.approval_rules.find_one({"processName": process_name})

    if approval_rule:
        approval_rule['rules'].extend(new_rules)
        current_app.mongo.db.approval_rules.update_one(
            {"processName": process_name},
            {"$set": {"rules": approval_rule['rules']}}
        )
        approval_rule['_id'] = str(approval_rule['_id'])
        return jsonify({"message": "Approval rule updated", "approval_rule": approval_rule}), 200
    else:
        new_approval_rule = {
            "processName": process_name,
            "rules": new_rules
        }
        current_app.mongo.db.approval_rules.insert_one(new_approval_rule)
        new_approval_rule['_id'] = str(new_approval_rule['_id'])
        return jsonify({"message": "Approval rule created", "approval_rule": new_approval_rule}), 201
