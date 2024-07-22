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
















# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId

# approval_rule_bp = Blueprint('approval_rules', __name__)

# @approval_rule_bp.route('/approval_rules', methods=['POST'])
# def add_approval_rule():
#     data = request.get_json()
#     process_id = data['processId']
#     conditions = data['conditions']  # Expecting an array of conditions with approvers

#     approval_rule = current_app.mongo.db.approval_rules.find_one({"processId": process_id})

#     new_rules = []
#     for condition in conditions:
#         condition_id = condition['conditionId']
#         approvers = condition['approvers']
        
#         new_rule = {
#             "conditionId": ObjectId(condition_id),
#             "approvers": approvers
#         }
#         new_rules.append(new_rule)

#     if approval_rule:
#         approval_rule['rules'].extend(new_rules)
#         current_app.mongo.db.approval_rules.update_one(
#             {"processId": process_id},
#             {"$set": {"rules": approval_rule['rules']}}
#         )
#         approval_rule['_id'] = str(approval_rule['_id'])
#         for rule in approval_rule['rules']:
#             if 'conditionId' in rule:
#                 rule['conditionId'] = str(rule['conditionId'])
#         return jsonify({"message": "Approval rule updated", "approval_rule": approval_rule}), 200
#     else:
#         new_approval_rule = {
#             "processId": process_id,
#             "rules": new_rules
#         }
#         current_app.mongo.db.approval_rules.insert_one(new_approval_rule)
#         new_approval_rule['_id'] = str(new_approval_rule['_id'])
#         for rule in new_approval_rule['rules']:
#             if 'conditionId' in rule:
#                 rule['conditionId'] = str(rule['conditionId'])
#         return jsonify({"message": "Approval rule created", "approval_rule": new_approval_rule}), 201














# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId

# approval_rule_bp = Blueprint('approval_rules', __name__)

# @approval_rule_bp.route('/approval_rules', methods=['POST'])
# def add_approval_rule():
#     data = request.get_json()
#     process_id = data['processId']
#     condition_refs = data['conditions']  # Expecting an array of condition references with approvers

#     # Fetch the conditions for the given processId from the conditions collection
#     condition_document = current_app.mongo.db.conditions.find_one({"processID": process_id})
#     if not condition_document:
#         return jsonify({"message": "Conditions not found for the given processId"}), 404

#     conditions = condition_document['conditions']

#     # Prepare the new rules using the conditions array indices
#     new_rules = []
#     for condition_ref in condition_refs:
#         condition_index = int(condition_ref['condition'].split('[')[1][:-1])
#         condition_data = conditions[condition_index]  # Fetch the condition using the index
#         approvers = condition_ref['approvers']
        
#         new_rule = {
#             "condition": condition_data,
#             "approvers": approvers
#         }
#         new_rules.append(new_rule)

#     # Check if the approval rule already exists
#     approval_rule = current_app.mongo.db.approval_rules.find_one({"processId": process_id})

#     if approval_rule:
#         approval_rule['rules'].extend(new_rules)
#         current_app.mongo.db.approval_rules.update_one(
#             {"processId": process_id},
#             {"$set": {"rules": approval_rule['rules']}}
#         )
#         approval_rule['_id'] = str(approval_rule['_id'])
#         return jsonify({"message": "Approval rule updated", "approval_rule": approval_rule}), 200
#     else:
#         new_approval_rule = {
#             "processId": process_id,
#             "rules": new_rules
#         }
#         current_app.mongo.db.approval_rules.insert_one(new_approval_rule)
#         new_approval_rule['_id'] = str(new_approval_rule['_id'])
#         return jsonify({"message": "Approval rule created", "approval_rule": new_approval_rule}), 201




















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
