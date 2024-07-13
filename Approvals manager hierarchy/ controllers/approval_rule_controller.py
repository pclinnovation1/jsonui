from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId

approval_rule_bp = Blueprint('approval_rule_bp', __name__)

@approval_rule_bp.route('/approval_rules', methods=['POST'])
def add_approval_rule():
    data = request.get_json()
    print("Print add approval")

    # Validate input data
    if not data:
        return jsonify({"message": "Invalid input"}), 400

    process_name = data.get('processName')
    if not process_name:
        return jsonify({"message": "processName is required"}), 400

    rules = data.get('rules')
    if not rules:
        return jsonify({"message": "rules are required"}), 400

    # Prepare the new rules
    new_rules = []
    for rule in rules:
        new_rule = {
            "levels": rule['levels'],
            "approverId": rule['approverId']
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
