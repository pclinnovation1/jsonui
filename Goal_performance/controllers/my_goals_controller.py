

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
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
    performance_goal = goals_collection.find_one({"goal_name": goal_name})
    if performance_goal:
        return performance_goal.get("employees", [])
    return []

@my_goals_bp.route('/', methods=['POST'])
def create_my_goal():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')

    # Fetch all goals for the given goal plan
    all_goals = get_goals_for_plan(goal_plan_name)

    goals_data = []
    for goal in all_goals:
        goal_name = goal.get("goal_name", "N/A")
        employees = get_employees_for_goal(goal_name)
        goals_data.append({
            "goal_name": goal_name,
            "employees": employees
        })

    # Create the document to insert into MongoDB
    my_goal_document = {
        'goal_plan_name': goal_plan_name,
        'goals': goals_data
    }

    goal_id = my_goals_collection.insert_one(my_goal_document).inserted_id
    new_goal = my_goals_collection.find_one({'_id': ObjectId(goal_id)})
    new_goal['_id'] = str(new_goal['_id'])

    return jsonify(new_goal), 201

@my_goals_bp.route('/', methods=['GET'])
def get_my_goals():
    my_goals = list(my_goals_collection.find())
    for goal in my_goals:
        goal['_id'] = str(goal['_id'])
    return jsonify(my_goals), 200

@my_goals_bp.route('/<goal_id>', methods=['GET'])
def get_my_goal(goal_id):
    my_goal = my_goals_collection.find_one({'_id': ObjectId(goal_id)})
    if my_goal:
        my_goal['_id'] = str(my_goal['_id'])
        return jsonify(my_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@my_goals_bp.route('/<goal_id>', methods=['PUT'])
def update_my_goal(goal_id):
    data = request.json
    result = my_goals_collection.update_one({'_id': ObjectId(goal_id)}, {'$set': data})
    if result.matched_count:
        updated_goal = my_goals_collection.find_one({'_id': ObjectId(goal_id)})
        updated_goal['_id'] = str(updated_goal['_id'])
        return jsonify(updated_goal), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404

@my_goals_bp.route('/<goal_id>', methods=['DELETE'])
def delete_my_goal(goal_id):
    result = my_goals_collection.delete_one({'_id': ObjectId(goal_id)})
    if result.deleted_count:
        return jsonify({'message': 'Goal deleted successfully'}), 200
    else:
        return jsonify({'error': 'Goal not found'}), 404
