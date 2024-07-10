# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId

# approver_bp = Blueprint('approver_bp', __name__)

# @approver_bp.route('/approvers', methods=['POST'])
# def create_approver():
#     data = request.json
#     approvers = current_app.mongo.db.approvers
#     approvers.insert_one(data)
#     return jsonify({"message": "Approver created successfully"}), 201

# @approver_bp.route('/approvers/<id>', methods=['GET'])
# def get_approver(id):
#     approvers = current_app.mongo.db.approvers
#     approver = approvers.find_one({"_id": ObjectId(id)})
#     return jsonify(approver), 200









from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId

approver_bp = Blueprint('approver_bp', __name__)

@approver_bp.route('/group', methods=['POST'])
def add_approval_group():
    data = request.get_json()
    approver = {
        "approverId": str(ObjectId()),
        "type": "group",
        "group": data['group'],
        "allowEmptyGroups": data['allowEmptyGroups'],
        "email": data['email']
    }
    current_app.mongo.db.approvers.insert_one(approver)
    approver['_id'] = str(approver['_id'])
    return jsonify({"message": "Approval group added", "approver": approver}), 201

@approver_bp.route('/hierarchy', methods=['POST'])
def add_management_hierarchy():
    data = request.get_json()
    approver = {
        "approverId": str(ObjectId()),
        "type": "hierarchy",
        "startsWith": data['startsWith'],
        "routesUsing": data['routesUsing'],
        "topApprover": data['topApprover'],
        "approvalChainOf": data['approvalChainOf'],
        "email": data['email']
    }
    current_app.mongo.db.approvers.insert_one(approver)
    approver['_id'] = str(approver['_id'])
    return jsonify({"message": "Management hierarchy added", "approver": approver}), 201

@approver_bp.route('/representative', methods=['POST'])
def add_representative():
    data = request.get_json()
    approver = {
        "approverId": str(ObjectId()),
        "type": "representative",
        "representativeType": data['representativeType'],
        "representativeOf": data['representativeOf'],
        "email": data['email']
    }
    current_app.mongo.db.approvers.insert_one(approver)
    approver['_id'] = str(approver['_id'])
    return jsonify({"message": "Representative added", "approver": approver}), 201

@approver_bp.route('/', methods=['GET'])
def get_approvers():
    approvers = list(current_app.mongo.db.approvers.find())
    for approver in approvers:
        approver['_id'] = str(approver['_id'])
    return jsonify({"approvers": approvers}), 200
