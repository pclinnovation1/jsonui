from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId

approver_bp = Blueprint('approver_bp', __name__)

@approver_bp.route('/manager_hierarchy', methods=['POST'])
def add_approvers_to_manager_hierarchy():
    data = request.get_json()
    print("Approver controler")

    # Validate input data
    if not data:
        return jsonify({"message": "Invalid input"}), 400
    
    process_name = data.get('processName')
    if not process_name:
        return jsonify({"message": "processName is required"}), 400
    
    approvers = data.get('approvers')
    if not approvers or not isinstance(approvers, list):
        return jsonify({"message": "approvers is required and must be a list"}), 400

    new_approvers = []
    for approver_data in approvers:
        levels = approver_data.get('levels')
        if not levels:
            return jsonify({"message": "levels is required for each approver"}), 400
        
        department = approver_data.get('department')
        if not department:
            return jsonify({"message": "department is required for each approver"}), 400
        
        employee_id = approver_data.get('employeeId')
        if not employee_id:
            return jsonify({"message": "employeeId is required for each approver"}), 400
        
        email = approver_data.get('email')
        if not email:
            return jsonify({"message": "email is required for each approver"}), 400

        approver_id = str(ObjectId())
        new_approver = {
            "approverId": approver_id,
            "levels": levels,
            "department": department,
            "employeeId": employee_id,
            "email": email
        }
        new_approvers.append(new_approver)

    # Insert new approvers
    current_app.mongo.db.approvers.insert_many(new_approvers)

    # Convert ObjectId to string before returning
    for approver in new_approvers:
        approver['_id'] = str(approver['_id'])

    return jsonify({"message": "Approvers added to manager hierarchy", "approvers": new_approvers}), 201
