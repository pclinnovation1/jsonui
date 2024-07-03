from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId

condition_bp = Blueprint('condition_bp', __name__)

@condition_bp.route('/conditions', methods=['POST'])
def add_condition():
    data = request.get_json()
    condition = {
        "conditionId": str(ObjectId()),
        "processId": data['processId'],
        "type": data['type'],
        "field": data['field'],
        "operator": data['operator'],
        "value": data['value'],
        "action": data['action']
    }
    current_app.mongo.db.conditions.insert_one(condition)
    condition['_id'] = str(condition['_id'])
    return jsonify({"message": "Condition added", "condition": condition}), 201

@condition_bp.route('/conditions', methods=['GET'])
def get_conditions():
    conditions = list(current_app.mongo.db.conditions.find())
    for condition in conditions:
        condition['_id'] = str(condition['_id'])
    return jsonify({"conditions": conditions}), 200
    