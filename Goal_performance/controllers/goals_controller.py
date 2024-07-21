
# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import config

# goals_bp = Blueprint('goals_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# goals_collection = db[config.GOALS_COLLECTION_NAME]

# @goals_bp.route('/', methods=['POST'])
# def create_goal():
#     data = request.json

#     if isinstance(data, list):
#         inserted_ids = goals_collection.insert_many(data).inserted_ids
#         new_goals = [goals_collection.find_one({'_id': _id}) for _id in inserted_ids]
#         for goal in new_goals:
#             goal['_id'] = str(goal['_id'])
#         return jsonify(new_goals), 201
#     else:
#         goal_id = goals_collection.insert_one(data).inserted_id
#         new_goal = goals_collection.find_one({'_id': goal_id})
#         new_goal['_id'] = str(new_goal['_id'])
#         return jsonify(new_goal), 201

# @goals_bp.route('/', methods=['GET'])
# def get_goals():
#     goals = list(goals_collection.find())
#     for goal in goals:
#         goal['_id'] = str(goal['_id'])
#     return jsonify(goals), 200

# @goals_bp.route('/<goal_id>', methods=['GET'])
# def get_goal(goal_id):
#     goal = goals_collection.find_one({'_id': ObjectId(goal_id)})
#     if goal:
#         goal['_id'] = str(goal['_id'])
#         return jsonify(goal), 200
#     else:
#         return jsonify({'error': 'Goal not found'}), 404

# @goals_bp.route('/<goal_id>', methods=['PUT'])
# def update_goal(goal_id):
#     data = request.json
#     result = goals_collection.update_one({'_id': ObjectId(goal_id)}, {'$set': data})
#     if result.matched_count:
#         updated_goal = goals_collection.find_one({'_id': ObjectId(goal_id)})
#         updated_goal['_id'] = str(updated_goal['_id'])
#         return jsonify(updated_goal), 200
#     else:
#         return jsonify({'error': 'Goal not found'}), 404

# @goals_bp.route('/<goal_id>', methods=['DELETE'])
# def delete_goal(goal_id):
#     result = goals_collection.delete_one({'_id': ObjectId(goal_id)})
#     if result.deleted_count:
#         return jsonify({'message': 'Goal deleted successfully'}), 200
#     else:
#         return jsonify({'error': 'Goal not found'}), 404



























from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

goals_bp = Blueprint('goals_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
employee_collection = db['s_employeedetails_2']  # Updated to the correct collection

# Helper function to get matching employees based on eligibility criteria
def get_matching_employees(eligibility_criteria):
    query = {}

    # Construct query based on non-null criteria fields in personal section
    personal_criteria = eligibility_criteria.get("personal", {})
    for key, value in personal_criteria.items():
        if value and value.lower() not in ["n/a", "all", "N/A", "All"]:
            field_name = key.replace(' ', '_')
            query[field_name] = value

    # Construct query based on non-null criteria fields in employment section
    employment_criteria = eligibility_criteria.get("employment", {})
    for key, value in employment_criteria.items():
        if value and value.lower() not in ["n/a", "all", "N/A", "All"]:
            field_name = key.replace(' ', '_')
            query[field_name] = value

    employees = employee_collection.find(query)
    employee_names = [
        f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        for employee in employees
    ]
    
    return employee_names

@goals_bp.route('/', methods=['POST'])
def create_goal():
    data = request.json

    if isinstance(data, list):
        for goal in data:
            eligibility_criteria = goal.get("eligibility_criteria", {})
            employees = get_matching_employees(eligibility_criteria)
            goal["employees"] = employees

        inserted_ids = goals_collection.insert_many(data).inserted_ids
        new_goals = [goals_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for goal in new_goals:
            goal['_id'] = str(goal['_id'])
        return jsonify(new_goals), 201
    else:
        eligibility_criteria = data.get("eligibility_criteria", {})
        employees = get_matching_employees(eligibility_criteria)
        data["employees"] = employees

        goal_id = goals_collection.insert_one(data).inserted_id
        new_goal = goals_collection.find_one({'_id': goal_id})
        new_goal['_id'] = str(new_goal['_id'])
        return jsonify(new_goal), 201

@goals_bp.route('/', methods=['GET'])
def get_goals():
    goals = list(goals_collection.find())
    for goal in goals:
        goal['_id'] = str(goal['_id'])
    return jsonify(goals), 200

@goals_bp.route('/<goal_id>', methods=['GET'])
def get_goal(goal_id):
    goal = goals_collection.find_one({'_id': ObjectId(goal_id)})
    if goal:
        goal['_id'] = str(goal['_id'])
        return jsonify(goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@goals_bp.route('/<goal_id>', methods=['PUT'])
def update_goal(goal_id):
    data = request.json
    eligibility_criteria = data.get("eligibility_criteria", {})
    employees = get_matching_employees(eligibility_criteria)
    data["employees"] = employees

    result = goals_collection.update_one({'_id': ObjectId(goal_id)}, {'$set': data})
    if result.matched_count:
        updated_goal = goals_collection.find_one({'_id': ObjectId(goal_id)})
        updated_goal['_id'] = str(updated_goal['_id'])
        return jsonify(updated_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@goals_bp.route('/<goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    result = goals_collection.delete_one({'_id': ObjectId(goal_id)})
    if result.deleted_count:
        return jsonify({'message': 'Goal deleted successfully'}), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404
