from flask import Blueprint, jsonify, request, current_app

condition_bp = Blueprint('condition_bp', __name__)

@condition_bp.route('/', methods=['POST'])
def create_condition():
    data = request.get_json()
    new_condition = {
        "condition_name": data['condition_name'],
        "statement": data['statement']
    }
    current_app.mongo.db.conditions.insert_one(new_condition)
    return jsonify({'message': 'Condition created successfully'}), 201

@condition_bp.route('/', methods=['GET'])
def get_conditions():
    conditions = current_app.mongo.db.conditions.find()
    return jsonify([condition for condition in conditions]), 200

@condition_bp.route('/<condition_name>', methods=['GET'])
def get_condition(condition_name):
    condition = current_app.mongo.db.conditions.find_one({"condition_name": condition_name})
    if condition is None:
        return jsonify({'message': 'Condition not found'}), 404
    return jsonify(condition), 200
