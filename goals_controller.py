# #goals_controller.py
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

#     # Validate and insert the goal data into MongoDB
#     goal_id = goals_collection.insert_one(data).inserted_id
#     new_goal = goals_collection.find_one({'_id': goal_id})
#     new_goal['_id'] = str(new_goal['_id'])

#     # Return the newly created goal
#     return jsonify(new_goal), 201

# @goals_bp.route('/', methods=['GET'])
# def get_goals():
#     # Retrieve all goals from the database
#     goals = list(goals_collection.find())
#     for goal in goals:
#         goal['_id'] = str(goal['_id'])
#     return jsonify(goals), 200

# @goals_bp.route('/<goal_id>', methods=['GET'])
# def get_goal(goal_id):
#     # Retrieve a specific goal by ID
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

@goals_bp.route('/', methods=['POST'])
def create_goal():
    data = request.json

    if isinstance(data, list):
        inserted_ids = goals_collection.insert_many(data).inserted_ids
        new_goals = [goals_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for goal in new_goals:
            goal['_id'] = str(goal['_id'])
        return jsonify(new_goals), 201
    else:
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
