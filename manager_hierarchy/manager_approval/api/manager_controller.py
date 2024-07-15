from flask import Blueprint, jsonify, request, current_app

manager_bp = Blueprint('manager_bp', __name__)

@manager_bp.route('/', methods=['POST'])
def create_manager():
    data = request.get_json()
    new_manager = {
        "manager_id": data['manager_id'],
        "manager_name": data['manager_name'],
        "department": data['department'],
        "experience": data['experience'],
        "level": data['level'],
        "email": data['email']
    }
    current_app.mongo.db.managers.insert_one(new_manager)
    return jsonify({'message': 'Manager created successfully'}), 201

@manager_bp.route('/', methods=['GET'])
def get_managers():
    managers = current_app.mongo.db.managers.find()
    return jsonify([manager for manager in managers]), 200

@manager_bp.route('/<manager_id>', methods=['GET'])
def get_manager(manager_id):
    manager = current_app.mongo.db.managers.find_one({"manager_id": manager_id})
    if manager is None:
        return jsonify({'message': 'Manager not found'}), 404
    return jsonify(manager), 200
