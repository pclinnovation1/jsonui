from flask import Blueprint, jsonify, request, current_app

employee_bp = Blueprint('employee_bp', __name__)

@employee_bp.route('/', methods=['POST'])
def create_employee():
    data = request.get_json()
    new_employee = {
        "employee_id": data['employee_id'],
        "employee_name": data['employee_name'],
        "department": data['department'],
        "experience": data['experience'],
        "email_id": data['email_id']  # New field added here
    }
    current_app.mongo.db.employees.insert_one(new_employee)
    return jsonify({'message': 'Employee created successfully'}), 201

@employee_bp.route('/', methods=['GET'])
def get_employees():
    employees = current_app.mongo.db.employees.find()
    return jsonify([employee for employee in employees]), 200

@employee_bp.route('/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = current_app.mongo.db.employees.find_one({"employee_id": employee_id})
    if employee is None:
        return jsonify({'message': 'Employee not found'}), 404
    return jsonify(employee), 200
