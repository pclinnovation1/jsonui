##colection PGM_my_goals

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

assign_goals_bp = Blueprint('assign_goals_bp', __name__)

# Connect to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
goal_plan_collection = db[config.GOAL_PLAN_COLLECTION_NAME]
goals_collection = db[config.GOALS_COLLECTION_NAME]
my_goals_collection = db[config.MY_GOALS_COLLECTION_NAME]

@assign_goals_bp.route('/', methods=['POST'])
def assign_goals_based_on_goal_eligibility():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')
    updated_by = data.get('updated_by', 'Unknown')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("Received goal_plan_name:", goal_plan_name)

    if not goal_plan_name:
        return jsonify({'error': 'Goal Plan Name is required'}), 400

    # Fetch the goal plan document based on the goal plan name
    goal_plan = goal_plan_collection.find_one({"details.goal_plan_name": goal_plan_name})
    print("Fetched goal plan:", goal_plan)

    if not goal_plan:
        return jsonify({'error': 'Goal Plan not found'}), 404

    # Retrieve the goal names from the goal plan
    goal_names = goal_plan.get("goals", [])
    print("Goal names in the goal plan:", goal_names)

    # Fetch the goals details from the goals collection
    goals = list(goals_collection.find({"basic_info.goal_name": {"$in": goal_names}}))
    print("Fetched goals details:", goals)

    if not goals:
        return jsonify({'error': 'No goals found for the specified goal plan'}), 404

    # Retrieve the combined employees from the goal plan
    combined_employees = set(goal_plan.get('combined_employees', []))
    print("Combined employees:", combined_employees)

    # Creating my_goals collection entries based on goal eligibility
    my_goals_entries = []
    for goal in goals:
        goal_name = goal["basic_info"]["goal_name"]
        eligible_employees = goal.get("employees", [])
        print(f"Processing goal: {goal_name}, Eligible employees: {eligible_employees}")

        # Filter combined employees based on eligible employees for this goal
        filtered_employees = [emp for emp in combined_employees if emp in eligible_employees]
        print(f"Eligible employees for goal {goal_name}:", filtered_employees)

        for employee_name in filtered_employees:
            my_goals_entry = {
                "name": employee_name,
                "goal_plan_assigned": goal_plan_name,
                "goal_name": goal_name,
                "progress": "Not started",
                "measurement": "None",
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






