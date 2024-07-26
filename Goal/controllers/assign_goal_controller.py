from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

add_goal_bp = Blueprint('add_goal_bp', __name__)

# Connect to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
my_goals_collection = db[config.MY_GOALS_COLLECTION_NAME]

@add_goal_bp.route('/', methods=['POST'])
def add_goal():
    data = request.json
    updated_by = data.get('updated_by', 'Unknown')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("Received data to add goal:", data)
    
    # Prepare the goal data
    goal_data = {
        "name": data.get("name"),
        "goal_plan_assigned": data.get("goal_plan_assigned","N/A"),
        "goal_name": data.get("goal_name"),
        "progress": data.get("progress", "Not started"),
        "measurement": data.get("measurement", "None"),
        "comments": data.get("comments", []),
        "feedback": data.get("feedback", []),
        "updated_by": updated_by,
        "created_at": current_time
    }
    
    print("Prepared goal data:", goal_data)
    
    # Insert the goal into the my_goals collection
    goal_id = my_goals_collection.insert_one(goal_data).inserted_id
    new_goal = my_goals_collection.find_one({'_id': goal_id})
    new_goal['_id'] = str(new_goal['_id'])
    
    print("Inserted new goal:", new_goal)
    return jsonify(new_goal), 201
