

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

goals_bp = Blueprint('goals_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
employee_collection = db['s_employeedetails_2']  # Ensure this is the correct collection

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

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")  # Capture updated_by from the request data

    if isinstance(data, list):
        for goal_data in data:
            goal = goal_data.get("goals", {})
            eligibility_criteria = goal.get("eligibility_criteria", {})
            employees = get_matching_employees(eligibility_criteria)
            goal["employees"] = employees
            goal["updated_date"] = current_time  # Set updated_date
            goal["updated_by"] = updated_by  # Set updated_by

            goal_data["goals"] = goal  # Update the goal data with employees and updated info

        inserted_ids = goals_collection.insert_many(data).inserted_ids
        new_goals = [goals_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for goal in new_goals:
            goal['_id'] = str(goal['_id'])
        return jsonify(new_goals), 201
    else:
        goal = data.get("goals", {})
        eligibility_criteria = goal.get("eligibility_criteria", {})
        employees = get_matching_employees(eligibility_criteria)
        goal["employees"] = employees
        goal["updated_date"] = current_time  # Set updated_date
        goal["updated_by"] = updated_by  # Set updated_by

        data["goals"] = goal  # Update the data with employees and updated info

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

@goals_bp.route('/<goal_name>', methods=['GET'])
def get_goal(goal_name):
    goal = goals_collection.find_one({'goals.basic_info.goal_name': goal_name})
    if goal:
        goal['_id'] = str(goal['_id'])
        return jsonify(goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@goals_bp.route('/<goal_name>', methods=['PUT'])
def update_goal(goal_name):
    data = request.json
    goal = data.get("goals", {})
    eligibility_criteria = goal.get("eligibility_criteria", {})
    employees = get_matching_employees(eligibility_criteria)
    goal["employees"] = employees

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")  # Capture updated_by from the request data
    goal["updated_date"] = current_time  # Update the updated_date field with the current date and time
    goal["updated_by"] = updated_by  # Update the updated_by field

    data["goals"] = goal  # Update the data with employees and updated info

    result = goals_collection.update_one({'goals.basic_info.goal_name': goal_name}, {'$set': data})
    if result.matched_count:
        updated_goal = goals_collection.find_one({'goals.basic_info.goal_name': goal_name})
        updated_goal['_id'] = str(updated_goal['_id'])
        return jsonify(updated_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@goals_bp.route('/<goal_name>', methods=['DELETE'])
def delete_goal(goal_name):
    result = goals_collection.delete_one({'goals.basic_info.goal_name': goal_name})
    if result.deleted_count:
        return jsonify({'message': 'Goal deleted successfully'}), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404
