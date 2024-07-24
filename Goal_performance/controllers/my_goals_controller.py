
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import config

my_goals_bp = Blueprint('my_goals_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
my_goals_collection = db[config.MY_GOALS_COLLECTION_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]

def get_goals_for_plan(goal_plan_name):
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})
    if goal_plan:
        return goal_plan.get("goals", [])
    return []

def get_employees_for_goal(goal_name):
    performance_goal = goals_collection.find_one({"goals.basic_info.goal_name": goal_name})
    if performance_goal:
        return performance_goal.get("goals", {}).get("employees", [])
    return []

def get_goal_details(goal_name):
    performance_goal = goals_collection.find_one({"goals.basic_info.goal_name": goal_name})
    if performance_goal:
        return performance_goal.get("goals", {})
    return {}

@my_goals_bp.route('/', methods=['POST'])
def create_my_goal():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')

    # Fetch all goals for the given goal plan
    all_goals = get_goals_for_plan(goal_plan_name)

    if not all_goals:
        return jsonify({"error": "No goals found for the provided goal plan name."}), 404

    my_goal_documents = []

    for goal in all_goals:
        goal_name = goal.get("goal_name", "N/A")
        employees = get_employees_for_goal(goal_name)
        goal_details = get_goal_details(goal_name)

        basic_info = goal_details.get("basic_info", {})
        start_date = basic_info.get("start_date")
        target_completion_date = basic_info.get("target_completion_date")

        # Get the most recent updated_date and updated_by
        updated_date = goal_details.get("measurements", {}).get("updated_date", datetime.utcnow())
        updated_by = goal_details.get("measurements", {}).get("updated_by", "Unknown")

        for employee in employees:
            my_goal_document = {
                "name": employee,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,
                "progress": goal_details.get("progress", "Not started"),
                "measurement": goal_details.get("measurement", "None"),
                "comments": goal_details.get("comments", []),
                "feedback": goal_details.get("feedback", []),
                "start_date": start_date,
                "target_completion_date": target_completion_date,
                "updated_date": updated_date,
                "updated_by": updated_by
            }
            my_goal_documents.append(my_goal_document)

    # Insert documents into MongoDB
    if my_goal_documents:
        inserted_ids = my_goals_collection.insert_many(my_goal_documents).inserted_ids
        new_goals = [my_goals_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for goal in new_goals:
            goal['_id'] = str(goal['_id'])
        return jsonify(new_goals), 201

    return jsonify({"error": "No documents were created."}), 500

@my_goals_bp.route('/', methods=['GET'])
def get_my_goals():
    my_goals = list(my_goals_collection.find())
    for goal in my_goals:
        goal['_id'] = str(goal['_id'])
    return jsonify(my_goals), 200

@my_goals_bp.route('/<goal_name>', methods=['GET'])
def get_my_goal(goal_name):
    my_goal = my_goals_collection.find_one({'goal_name': goal_name})
    if my_goal:
        my_goal['_id'] = str(my_goal['_id'])
        return jsonify(my_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@my_goals_bp.route('/<goal_name>', methods=['PUT'])
def update_my_goal(goal_name):
    data = request.json
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")
    data["updated_date"] = current_time
    data["updated_by"] = updated_by

    result = my_goals_collection.update_one({'goal_name': goal_name}, {'$set': data})
    if result.matched_count:
        updated_goal = my_goals_collection.find_one({'goal_name': goal_name})
        updated_goal['_id'] = str(updated_goal['_id'])
        return jsonify(updated_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@my_goals_bp.route('/<goal_name>', methods=['DELETE'])
def delete_my_goal(goal_name):
    result = my_goals_collection.delete_one({'goal_name': goal_name})
    if result.deleted_count:
        return jsonify({'message': 'Goal deleted successfully'}), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404
