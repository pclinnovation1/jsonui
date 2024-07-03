# from flask import Blueprint, request, jsonify, current_app
# from bson import ObjectId

# approval_rule_bp = Blueprint('approval_rule_bp', __name__)

# @approval_rule_bp.route('/approval_rules', methods=['POST'])
# def add_approval_rule():
#     data = request.get_json()
#     process_id = data['processId']
    
#     # Check if a rule for this process already exists
#     existing_rule = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
    
#     new_rule = {
#         "ruleId": str(ObjectId()),
#         "condition": data['condition'],
#         "approvers": data['approvers']
#     }
    
#     if existing_rule:
#         # Ensure the 'rules' key exists
#         if 'rules' not in existing_rule:
#             existing_rule['rules'] = []
        
#         # Add new condition and approvers to the existing rule
#         existing_rule['rules'].append(new_rule)
#         current_app.mongo.db.approval_rules.update_one(
#             {"processId": process_id},
#             {"$set": {"rules": existing_rule['rules']}}
#         )
#         # Convert ObjectId to string for JSON serialization
#         existing_rule['_id'] = str(existing_rule['_id'])
#         for rule in existing_rule['rules']:
#             rule['ruleId'] = str(rule['ruleId'])
#         return jsonify({"message": "Approval rule updated", "approval_rule": existing_rule}), 200
#     else:
#         # Create a new approval rule
#         approval_rule = {
#             "processId": process_id,
#             "rules": [new_rule]
#         }
#         current_app.mongo.db.approval_rules.insert_one(approval_rule)
#         approval_rule['_id'] = str(approval_rule['_id'])
#         return jsonify({"message": "Approval rule added", "approval_rule": approval_rule}), 201

# @approval_rule_bp.route('/approval_rules', methods=['GET'])
# def get_approval_rules():
#     approval_rules = list(current_app.mongo.db.approval_rules.find())
#     for rule in approval_rules:
#         rule['_id'] = str(rule['_id'])
#         for r in rule.get('rules', []):
#             r['ruleId'] = str(r['ruleId'])
#     return jsonify({"approval_rules": approval_rules}), 200




















from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId

approval_rule_bp = Blueprint('approval_rules', __name__)

@approval_rule_bp.route('/approval_rules', methods=['POST'])
def add_approval_rule():
    data = request.get_json()
    process_id = data['processId']
    conditions = data['conditions']  # Expecting an array of conditions with approvers

    approval_rule = current_app.mongo.db.approval_rules.find_one({"processId": process_id})

    new_rules = []
    for condition in conditions:
        condition_id = condition['conditionId']
        approvers = condition['approvers']
        
        new_rule = {
            "conditionId": ObjectId(condition_id),
            "approvers": approvers
        }
        new_rules.append(new_rule)

    if approval_rule:
        approval_rule['rules'].extend(new_rules)
        current_app.mongo.db.approval_rules.update_one(
            {"processId": process_id},
            {"$set": {"rules": approval_rule['rules']}}
        )
        approval_rule['_id'] = str(approval_rule['_id'])
        for rule in approval_rule['rules']:
            if 'conditionId' in rule:
                rule['conditionId'] = str(rule['conditionId'])
        return jsonify({"message": "Approval rule updated", "approval_rule": approval_rule}), 200
    else:
        new_approval_rule = {
            "processId": process_id,
            "rules": new_rules
        }
        current_app.mongo.db.approval_rules.insert_one(new_approval_rule)
        new_approval_rule['_id'] = str(new_approval_rule['_id'])
        for rule in new_approval_rule['rules']:
            if 'conditionId' in rule:
                rule['conditionId'] = str(rule['conditionId'])
        return jsonify({"message": "Approval rule created", "approval_rule": new_approval_rule}), 201
