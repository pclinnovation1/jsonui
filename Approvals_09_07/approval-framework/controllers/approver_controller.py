

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

# @approver_bp.route('/hierarchy', methods=['POST'])
# def add_management_hierarchy():
#     data = request.get_json()
#     approver = {
#         "approverId": str(ObjectId()),
#         "type": "hierarchy",
#         "startsWith": data['startsWith'],
#         "routesUsing": data['routesUsing'],
#         "topApprover": data['topApprover'],
#         "approvalChainOf": data['approvalChainOf'],
#         "email": data['email']
#     }
#     current_app.mongo.db.approvers.insert_one(approver)
#     approver['_id'] = str(approver['_id'])
#     return jsonify({"message": "Management hierarchy added", "approver": approver}), 201


@approver_bp.route('/hierarchy', methods=['POST'])
def setup_hierarchy():
    db=current_app.mongo.db
    # Parse JSON data
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': 'Invalid JSON data', 'message': str(e)}), 400
    
    print("*" * 25)
    print("data from mongodb: ", data)
    print("*" * 25)

    department = data['department']

    lavel = set()
    lavel.add(int(data['start_with']))

    # Query for managers in the given department
    managers = list(db.managers.find({"department": department}))
    
    # Log the managers found
    print("Managers found in department '{}':".format(department))
    for manager in managers:
        print(manager)
    
    manager_levels = {int(manager['lavels']) for manager in managers}

    if len(lavel) < int(data["number_of_levels"]) and int(data["route_using"]) in manager_levels:
        lavel.add(int(data["route_using"]))

    # Check and add top approver's level if it exists in manager_levels
    if len(lavel) < int(data["number_of_levels"]) and int(data["top_approver"]) in manager_levels:
        lavel.add(int(data["top_approver"]))

    i = int(data['start_with'])
    while len(lavel) < int(data["number_of_levels"]):
        lavel.add(i)
        i += 1

    print('lavel : ', lavel)

    emails = []
    for manager in managers:
        print('manager : ', manager)
        print('lavel', lavel)

        if int(manager['lavels']) in lavel:
            emails.append(manager['email'])

    hierarchy_data = {
        "approverId": str(ObjectId()),
        "type": "management hierarchy",
        'department': data['department'],
        'route_using': data['route_using'],
        'approval_chain_of': data['approval_chain_of'],
        'start_with': data['start_with'],
        'number_of_levels': data['number_of_levels'],
        'top_approver': data['top_approver'],
        'lavels_for_approvel':list(lavel),
        'email': emails
    }

    print("*" * 25)
    print("hierarchy_data ", hierarchy_data)
    print("*" * 25)

    # Insert data into MongoDB
    result = db.approvers.insert_one(hierarchy_data)
    hierarchy_data['_id'] = str(hierarchy_data['_id'])
    return jsonify({"message": "Representative added", "approver": hierarchy_data}), 201


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
