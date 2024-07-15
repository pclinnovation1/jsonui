from flask import Blueprint, jsonify, request, current_app

approval_bp = Blueprint('approval_bp', __name__)

@approval_bp.route('/', methods=['POST'])
def create_approval():
    data = request.get_json()
    new_approval = {
        "approval_id": data['approval_id'],
        "approval_name": data['approval_name'],
        "department": data['department'],
        "status": data['status']
    }
    current_app.mongo.db.approvals.insert_one(new_approval)
    return jsonify({'message': 'Approval created successfully'}), 201

@approval_bp.route('/', methods=['GET'])
def get_approvals():
    approvals = current_app.mongo.db.approvals.find()
    return jsonify([approval for approval in approvals]), 200

@approval_bp.route('/<approval_id>', methods=['GET'])
def get_approval(approval_id):
    approval = current_app.mongo.db.approvals.find_one({"approval_id": approval_id})
    if approval is None:
        return jsonify({'message': 'Approval not found'}), 404
    return jsonify(approval), 200
