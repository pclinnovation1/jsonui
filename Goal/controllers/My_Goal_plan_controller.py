##collection PGM_my_goal_plan_goals

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

my_goal_plan_bp = Blueprint('my_goal_plan_bp', __name__)

# Connect to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
my_goals_collection = db[config.MY_GOAL_PLAN_COLLECTION_NAME]  # Fixed typo in collection name

@my_goal_plan_bp.route('/', methods=['POST'])
def fetch_goals():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')
    updated_by = data.get('updated_by', 'Unknown')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("goal_plan_name:", goal_plan_name)

    if not goal_plan_name:
        return jsonify({'error': 'Goal Plan Name is required'}), 400

    # Fetching the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})

    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404

    # Fetch combined employees list
    combined_employees = set(goal_plan.get('combined_employees', []))
    print("Combined employees:", combined_employees)

    # Retrieve the goal names
    goals = goal_plan.get('goals', [])
    print("Goals:", goals)

    # Creating my_goals collection entries
    my_goals_entries = []
    for employee_name in combined_employees:
        for goal_name in goals:
            my_goals_entry = {
                "name": employee_name,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,
                "progress": "Not started",  # Default value
                "measurement": "None",  # Default value
                "comments": [],
                "feedback": [],
                "updated_by": updated_by,
                "created_at": current_time

            }
            print("Created my_goals entry:", my_goals_entry)
            my_goals_entries.append(my_goals_entry)

    # Insert into my_goals collection
    if my_goals_entries:
        print("Inserting entries into my_goals collection")
        result = my_goals_collection.insert_many(my_goals_entries)
        inserted_ids = result.inserted_ids
        print("Inserted IDs:", inserted_ids)
        # Retrieve the newly inserted documents to include in the response
        my_goals_entries = list(my_goals_collection.find({"_id": {"$in": inserted_ids}}))

    # Convert ObjectIds to strings
    for entry in my_goals_entries:
        entry['_id'] = str(entry['_id'])
        print("Converted entry:", entry)

    print("Final my_goals_entries:", my_goals_entries)
    return jsonify({'message': 'Goals successfully assigned', 'my_goals': my_goals_entries}), 200







